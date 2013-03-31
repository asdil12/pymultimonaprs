#!/usr/bin/python2

import json
import threading
from time import sleep

import multimon
import beacon
import gate
from frame import APRSFrame

config = json.load(open('config.json'))


def mmcb(ui_frame):
	frame = APRSFrame()
	frame.import_ui(ui_frame)
	tnc2_frame = frame.export_tnc2()
	ig.send(tnc2_frame)

def bc():
	bcargs = {
		'lat': config['beacon']['lat'],
		'lng': config['beacon']['lng'],
		'callsign': config['callsign'],
		'table': config['beacon']['table'],
		'symbol': config['beacon']['symbol'],
		'comment': config['beacon']['comment'],
	}
	while True:
		tnc2_frame = beacon.get_beacon_frame(**bcargs)
		ig.send(tnc2_frame)
		tnc2_frame = beacon.get_status_frame(config['callsign'], config['beacon']['status'])
		ig.send(tnc2_frame)
		sleep(config['beacon']['send_every'])


ig = gate.IGate(config['callsign'], config['passcode'], config['gateway'])

mmt = threading.Thread(target=multimon.multimon, args=(mmcb,config))
mmt.setDaemon(True)
mmt.start()

#bct = threading.Thread(target=bc)
#bct.setDaemon(True)
#bct.start()

bc()

