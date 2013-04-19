#!/usr/bin/python2

import threading
import subprocess
import re

start_frame_re = re.compile(r'^AFSK1200: (.*)$')
aprs_datatypes = [0x1C, 0x1D, '!', '=', ')', ';', '@', '/', '>', '\'', '`']

class Multimon:
	def __init__(self, frame_handler, config):
		self.frame_handler = frame_handler
		self.config = config
		self.subprocs = {}
		self._start()
		self._running = True
		self._worker = threading.Thread(target=self._mm_worker)
		self._worker.setDaemon(True)
		self._worker.start()

	def exit(self):
		self._running = False
		self._stop()

	def _start(self):
		if self.config['source'] == 'pulse':
			proc_mm = subprocess.Popen(
				['multimonNG', '-a', 'AFSK1200'],
				stdout=subprocess.PIPE, stderr=open('/dev/null')
			)
		else:
			if self.config['source'] == 'rtl':
				proc_src = subprocess.Popen(
					['rtl_fm', '-f', str(int(self.config['rtl']['freq'] * 1e6)), '-s', '22050',
					'-p', str(self.config['rtl']['ppm']), '-g', str(self.config['rtl']['gain']), '-'],
					stdout=subprocess.PIPE, stderr=open('/dev/null')
				)
			elif self.config['source'] == 'alsa':
				proc_src = subprocess.Popen(
					['arecord', '-D', self.config['alsa']['device'],
					'-r', '22050', '-f', 'S16_LE', '-t', 'raw', '-c', '1', '-'],
					stdout=subprocess.PIPE, stderr=open('/dev/null')
				)
			proc_mm = subprocess.Popen(
				['multimonNG', '-a', 'AFSK1200', '-'],
				stdin=proc_src.stdout,
				stdout=subprocess.PIPE, stderr=open('/dev/null')
			)
			self.subprocs['src'] = proc_src
		self.subprocs['mm'] = proc_mm

	def _stop(self):
		for name in ['mm', 'src']:
			try:
				proc = self.subprocs[name]
				proc.terminate()
			except:
				pass

	def _mm_worker(self):
		awaiting_payload = False
		frame_buffer = ''

		while self._running:
			line = self.subprocs['mm'].stdout.readline()
			line = line.strip()
			m = start_frame_re.match(line)
			if m:
				awaiting_payload = True
				frame_buffer = "%s\n" % m.group(1)
			elif awaiting_payload:
				awaiting_payload = False
				if line[0] in aprs_datatypes:
					frame_buffer += line
					self.frame_handler(frame_buffer)
