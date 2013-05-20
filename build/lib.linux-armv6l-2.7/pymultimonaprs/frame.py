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

	def import_ui(self, uiframe):
		uiframe = uiframe.replace("\r", "")
		header, payload = uiframe.split(":", 1)
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

	def export_tnc2(self):
		tnc2 = "%s>%s,%s:%s" % (self.source, self.dest, ','.join(self.path), self.payload)
		if len(tnc2) > 510:
			tnc2 = tnc2[:510]
		return tnc2
