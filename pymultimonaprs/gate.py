#!/usr/bin/env python3

import threading
import socket
import queue
import pkg_resources
import logging
import errno
import itertools
from time import sleep

class IGate:
    def __init__(self, callsign, passcode, gateways, preferred_protocol):
        self.log = logging.getLogger('pymultimonaprs')
        if isinstance(gateways, list):  # Verwenden von isinstance anstelle von type
            self.gateways = itertools.cycle(gateways)
            self.gateway = False
        else:
            self.gateway = gateways  # alte Konfiguration, einzelner Hostname als String
        self.callsign = callsign
        self.passcode = passcode
        self.preferred_protocol = preferred_protocol
        self.socket = None
        self._sending_queue = queue.Queue(maxsize=1)
        self._connect()
        self._running = True
        self._worker = threading.Thread(target=self._socket_worker)
        self._worker.setDaemon(True)
        self._worker.start()

    def exit(self):
        self._running = False
        self._disconnect()

    def _connect(self):
        connected = False
        while not connected:
            try:
                # Verbinden
                gateway = self.gateway or next(self.gateways)
                if gateway.startswith("["):
                    self.server, self.port = gateway.lstrip("[").split("]:")
                else:
                    self.server, self.port = gateway.split(':')
                self.port = int(self.port)

                if self.preferred_protocol == 'ipv6':
                    addrinfo = socket.getaddrinfo(self.server, self.port, socket.AF_INET6)
                elif self.preferred_protocol == 'ipv4':
                    addrinfo = socket.getaddrinfo(self.server, self.port, socket.AF_INET)
                else:
                    addrinfo = socket.getaddrinfo(self.server, self.port)

                self.socket = socket.socket(*addrinfo[0][0:3])
                self.log.info("connecting... %s:%i", addrinfo[0][4], self.port)
                self.socket.connect(addrinfo[0][4])
                self.log.info("connected")

                server_hello = self.socket.recv(1024)
                self.log.info(server_hello.strip(b" \r\n").decode('utf8'))

                # Versuch, meine Version zu erhalten
                try:
                    version = pkg_resources.get_distribution("pymultimonaprs").version
                except Exception:
                    version = 'GIT'

                # Anmeldung
                self.log.info("login %s (PyMultimonAPRS %s)", self.callsign, version)
                self.socket.sendall(f"user {self.callsign} pass {self.passcode} vers PyMultimonAPRS {version} filter r/38/-171/1\r\n".encode('utf-8'))

                server_return = self.socket.recv(1024)
                self.log.info(server_return.strip(b" \r\n").decode('utf8'))

                connected = True
            except socket.error as e:
                self.log.warning("Error when connecting to %s:%d: '%s'", self.server, self.port, str(e))
                sleep(1)

    def _disconnect(self):
        try:
            self.socket.close()
        except Exception:
            pass

    def send(self, frame):
        try:
            # warten Sie 10 Sekunden auf einen Queue-Slot und verwerfen Sie die Daten
            self._sending_queue.put(frame, True, 10)
        except queue.Full:
            self.log.warning("Lost TX data (queue full): '%s'", frame.export(False))

    def _socket_worker(self):
        """
        Fährt als Thread, liest aus dem Socket, sendet die Warteschlange zum Socket
        """
        while self._running:
            try:
                try:
                    # max. 1 Sekunde auf neue Daten warten
                    frame = self._sending_queue.get(True, 1)
                    self.log.debug("sending: %s", frame.export(False))
                    raw_frame = f"{frame.export()}\r\n"
                    totalsent = 0
                    while totalsent < len(raw_frame):
                        sent = self.socket.send(raw_frame[totalsent:].encode('utf-8'))  # encode in UTF-8
                        if sent == 0:
                            raise socket.error(0, "Failed to send data - number of sent bytes: 0")
                        totalsent += sent
                except queue.Empty:
                    pass

                # (versuchen) vom Socket zu lesen, um ein Überlaufen des Puffers zu verhindern
                self.socket.setblocking(0)
                try:
                    res = self.socket.recv(40960)
                except socket.error as e:
                    if not e.errno == errno.EAGAIN:
                        # Wenn der Fehler etwas anderes als 'rx Queue leer' ist
                        raise
                self.socket.setblocking(1)
            except socket.error as e:
                # Mögliche Fehler beim I/O:
                # [Errno11] Buffer is empty (maybe not when using blocking sockets)
                # [Errno32] Broken Pipe
                # [Errno 104] Connection reset by peer
                # [Errno 110] Connection time out
                if e.errno in {errno.EAGAIN, errno.EWOULDBLOCK}:
                    # Verhindern Sie das Wiederherstellen bei diesen Fehlern
                    sleep(1)
                else:
                    self.log.warning("Connection issue: '%s'", str(e))
                    sleep(1)
                    # Versuchen Sie, sich erneut zu verbinden
                    self._connect()
        self.log.debug("sending thread exit")

