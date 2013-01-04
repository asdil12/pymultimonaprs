#!/usr/bin/python2

import subprocess
import re

def multimon(frame_handler):
	start_frame_re = re.compile(r'^AFSK1200: (.*)$')

	aprs_datatypes = [0x1C, 0x1D, '!', '=', ')', ';', '@', '/', '>', '\'', '`']

	proc = subprocess.Popen(['multimonNG', '-a', 'AFSK1200'], stdout=subprocess.PIPE, stderr=open('/dev/null'))

	awaiting_payload = False
	frame_buffer = ''

	while True:
		line = proc.stdout.readline()
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

