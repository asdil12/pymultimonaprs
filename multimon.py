#!/usr/bin/python2

import subprocess
import re

def multimon(frame_handler, config):
	start_frame_re = re.compile(r'^AFSK1200: (.*)$')

	aprs_datatypes = [0x1C, 0x1D, '!', '=', ')', ';', '@', '/', '>', '\'', '`']

	if config['source'] == 'pulse':
		proc_mm = subprocess.Popen(['multimonNG', '-a', 'AFSK1200'], stdout=subprocess.PIPE, stderr=open('/dev/null'))
	else:
		if config['source'] == 'rtl':
			proc_src = subprocess.Popen(
				['rtl_fm', '-f', str(int(config['rtl']['freq'] * 1e6)), '-s', '22050', '-p', str(config['rtl']['ppm']), '-g', str(config['rtl']['gain']), '-'],
				stdout=subprocess.PIPE, stderr=open('/dev/null')
			)
		elif config['source'] == 'alsa':
			proc_src = subprocess.Popen(
				['arecord', '-D', config['alsa']['device'], '-r', '22050', '-f', 'S16_LE', '-t', 'raw', '-c', '1', '-'],
				stdout=subprocess.PIPE, stderr=open('/dev/null')
			)
		proc_mm = subprocess.Popen(
			['multimonNG', '-a', 'AFSK1200', '-'],
			stdin=proc_src.stdout,
			stdout=subprocess.PIPE, stderr=open('/dev/null')
		)

	awaiting_payload = False
	frame_buffer = ''

	while True:
		line = proc_mm.stdout.readline()
		line = line.strip()
		m = start_frame_re.match(line)
		if m:
			awaiting_payload = True
			frame_buffer = "%s\n" % m.group(1)
		elif awaiting_payload:
			awaiting_payload = False
			if line[0] in aprs_datatypes:
				frame_buffer += line
				frame_handler(frame_buffer)

