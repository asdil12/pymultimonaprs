#!/usr/bin/python2

import re

header_re = re.compile(r'^(?P<source>\w*(-\d{1,2})?)>(?P<dest>\w*(-\d{1,2})?),(?P<path>[^\s]*)')

class InvalidFrame(Exception):
	pass

class APRSFrame:
	def __init__(self):
		self.source = None
		self.dest = None
		self.path = []
		self.payload = unicode()

	def import_tnc2(self, tnc2_frame, decode=True):
		if decode:
			tnc2_frame = tnc2_frame.decode('ISO-8859-1')
		tnc2_frame = tnc2_frame.replace("\r", "")
		header, payload = tnc2_frame.split(":", 1)
		header = header.strip()
		payload = payload.strip()
		try:
			res = header_re.match(header).groupdict()
			self.source = res['source']
			self.dest = res['dest']
			self.path = res['path'].split(',')
		except:
			raise InvalidFrame()
		self.payload = payload

	def export(self, encode=True):
		tnc2 = "%s>%s,%s:%s" % (self.source, self.dest, ','.join(self.path), self.payload)
		if len(tnc2) > 510:
			tnc2 = tnc2[:510]
		if encode:
			tnc2 = tnc2.encode('ISO-8859-1')
		return tnc2
