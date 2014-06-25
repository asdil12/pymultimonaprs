#!/usr/bin/python2

import os
import json
from datetime import datetime
from pymultimonaprs.frame import APRSFrame

def process_ambiguity(pos, ambiguity):
	num = bytearray(pos)
	for i in range(0, ambiguity):
		if i > 1:
			# skip the dot
			i += 1
		# skip the direction
		i += 2
		num[-i] = " "
	return str(num)

def encode_lat(lat):
	lat_dir = 'N' if lat > 0 else 'S'
	lat_abs = abs(lat)
	lat_deg = int(lat_abs)
	lat_min = (lat_abs % 1) * 60
	return "%02i%05.2f%c" % (lat_deg, lat_min, lat_dir)

def encode_lng(lng):
	lng_dir = 'E' if lng > 0 else 'W'
	lng_abs = abs(lng)
	lng_deg = int(lng_abs)
	lng_min = (lng_abs % 1) * 60
	return "%03i%05.2f%c" % (lng_deg, lng_min, lng_dir)

def mkframe(callsign, payload):
	frame = APRSFrame()
	frame.source = callsign
	frame.dest = u'APRS'
	frame.path = [u'TCPIP*']
	frame.payload = payload
	return frame

def get_beacon_frame(lat, lng, callsign, table, symbol, comment, ambiguity):
	enc_lat = process_ambiguity(encode_lat(lat), ambiguity)
	enc_lng = process_ambiguity(encode_lng(lng), ambiguity)
	pos = "%s%s%s" % (enc_lat, table, enc_lng)
	payload = "=%s%s%s" % (pos, symbol, comment)
	return mkframe(callsign, payload)

def get_status_frame(callsign, status):
	try:
		if status['file'] and os.path.exists(status['file']):
			status_text = open(status['file']).read().decode('UTF-8').strip()
		elif status['text']:
			status_text = status['text']
		else:
			return None
		payload = ">%s" % status_text
		return mkframe(callsign, payload)
	except:
		return None

def get_weather_frame(callsign, weather):
	try:
		w = json.load(open(weather))

		# Convert to imperial and encode

		# Timestamp
		wenc = datetime.utcfromtimestamp(int(w['timestamp'])).strftime('%m%d%H%M')

		# Wind
		wind = w.get('wind', {})
		if 'direction' in wind:
			wenc += "c%03d" % wind['direction']
		else:
			wenc += "c..."
		if 'speed' in wind:
			si = round(wind['speed'] * 0.621371192)
			wenc += "s%03d" % si
		else:
			wenc += "s..."
		if 'gust' in wind:
			si = round(wind['gust'] * 0.621371192)
			wenc += "g%03d" % si
		else:
			wenc += "g..."

		# Temperature
		if 'temperature' in w:
			wenc += "t%03d" % round(w['temperature'] / (float(5)/9) + 32)
		else:
			wenc += "t..."

		# Humidity
		if 'humidity' in w:
			h = w['humidity']
			if h == 0: h = 1
			if h == 100: h = 0
			wenc += "h%02d" % h
		else:
			wenc += "h.."

		# Atmospheric pressure
		if 'pressure' in w:
			wenc += "b%04d" % round(w['pressure'] * 10)

		payload = "_%sPyMM" % wenc
		return mkframe(callsign, payload)
	except:
		return None
