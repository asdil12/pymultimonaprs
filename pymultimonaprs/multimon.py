#!/usr/bin/env python3

import threading
import subprocess
import re
import os

start_frame_re = re.compile(r'^APRS: (.*)')

class Multimon:
    def __init__(self, frame_handler, config):
        self.frame_handler = frame_handler
        self.config = config
        self.subprocs = {}
        self._start()
        self._running = True
        self._worker = threading.Thread(target=self._mm_worker)
        self._worker.daemon = True  # Update to use daemon property directly
        self._worker.start()

    def exit(self):
        self._running = False
        self._stop()

    def _start(self):
        if self.config['source'] == 'pulse':
            proc_mm = subprocess.Popen(
                ['multimon-ng', '-a', 'AFSK1200', '-A'],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
        else:
            if self.config['source'] == 'rtl':
                proc_src = subprocess.Popen(
                    ['rtl_fm', '-f', str(int(self.config['rtl']['freq'] * 1e6)), '-s', '22050',
                     '-p%s' % str(self.config['rtl']['ppm']), '-g', str(self.config['rtl']['gain']),
                     '-E', 'offset' if self.config['rtl'].get('offset_tuning', False) else 'none',
                     '-d', str(self.config['rtl'].get('device_index', 0)), '-'],
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
                )
            elif self.config['source'] == 'alsa':
                proc_src = subprocess.Popen(
                    ['arecord', '-D', self.config['alsa']['device'],
                     '-r', '22050', '-f', 'S16_LE', '-t', 'raw', '-c', '1', '-'],
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
                )
            proc_mm = subprocess.Popen(
                ['multimon-ng', '-a', 'AFSK1200', '-A', '-t', 'raw', '-'],
                stdin=proc_src.stdout,
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            self.subprocs['src'] = proc_src
        self.subprocs['mm'] = proc_mm

    def _stop(self):
        for name in ['mm', 'src']:
            try:
                proc = self.subprocs[name]
                proc.terminate()
            except KeyError:
                pass
            except Exception as e:
                print(f"Error stopping process {name}: {e}")

    def _mm_worker(self):
        while self._running:
            line = self.subprocs['mm'].stdout.readline()
            line = line.strip().decode('utf-8')  # Decode bytes to string
            m = start_frame_re.match(line)
            if m:
                tnc2_frame = m.group(1)
                self.frame_handler(tnc2_frame)
