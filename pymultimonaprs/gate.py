#!/usr/bin/python2

import threading
import socket
import Queue
import pkg_resources
import sys
import logging
import select
import errno
from time import sleep

class IGate:
	def __init__(self, callsign, passcode, gateway):
		self.log = logging.getLogger('pymultimonaprs')
		self.server, self.port = gateway.split(':')
		self.port = int(self.port)
		self.callsign = callsign
		self.passcode = passcode
		self.socket = None
		self._sending_queue = Queue.Queue(maxsize=1)
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
				# Connect
				self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				ip = socket.gethostbyname(self.server)
				self.log.info("connecting... %s:%i" % (ip, self.port))
				self.socket.connect((ip, self.port))
				self.log.info("connected")

				server_hello = self.socket.recv(1024)
				self.log.info(server_hello.strip(" \r\n"))

				# Try to get my version
				try:
					version = pkg_resources.get_distribution("pymultimonaprs").version
				except:
					version = 'GIT'

				# Login
				self.log.info("login %s (PyMultimonAPRS %s)" % (self.callsign, version))
				self.socket.send("user %s pass %s vers PyMultimonAPRS %s filter r/38/-171/1\r\n" %
						(self.callsign, self.passcode, version))

				server_return = self.socket.recv(1024)
				self.log.info(server_return.strip(" \r\n"))

				connected = True
			except socket.error as e:
				self.log.warn("Error when connecting to server: '%s'" % str(e))
				sleep(1)

	def _disconnect(self):
		try:
			self.socket.close()
		except:
			pass

			# wait 10sec for queue slot, then drop the data
	def send(self, frame):
		try:
			self._sending_queue.put(frame, True, 10)
		except Queue.Full as e:
			self.log.warn("Lost TX data (queue full): '%s'" % frame.export(False))

	def _socket_worker(self):
		"""
		Running as a thread, reading from socket, sending queue to socket
		"""
		while self._running:
			try:
				try:
					# wait max 1sec for new data
					frame = self._sending_queue.get(True, 1)
					self.log.debug("sending: %s" % frame.export(False))
					raw_frame = "%s\r\n" % frame.export()
					totalsent = 0
					while totalsent < len(raw_frame):
						sent = self.socket.send(raw_frame[totalsent:])
						if sent == 0:
							raise socket.error(0, "Failed to send data - number of sent bytes: 0")
						totalsent += sent
				except Queue.Empty:
					pass

				# (try to) read from socket to prevent buffer fillup
				self.socket.setblocking(0)
				try:
					res = self.socket.recv(40960)
				except socket.error as e:
					if not e.errno == 11:
						# if the error is other than 'rx queue empty'
						raise
				self.socket.setblocking(1)
			except socket.error as e:
				# possible errors on io:
				# [Errno  11] Buffer is empty (maybe not when using blocking sockets)
				# [Errno  32] Broken Pipe
				# [Errno 104] Connection reset by peer
				# [Errno 110] Connection time out
				if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
					# prevent reconnecting on these errors
					sleep(1)
				else:
					self.log.warn("Connection issue: '%s'" % str(e))
					sleep(1)
					# try to reconnect
					self._connect()
		self.log.debug("sending thread exit")
