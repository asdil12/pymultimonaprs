#!/usr/bin/python2

import os
import json
from datetime import datetime

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

def get_beacon_frame(lat, lng, callsign, table, symbol, comment):
	pos = "%s%s%s" % (encode_lat(lat), table, encode_lng(lng))
	payload = "=%s%s %s" % (pos, symbol, comment)
	return "%s>APRS,TCPIP*:%s" % (callsign, payload)

def get_status_frame(callsign, status):
	try:
		if status['file'] and os.path.exists(status['file']):
			status_text = open(status['file']).read().strip()
		elif status['text']:
			status_text = status['text']
		else:
			return None
		payload = ">%s" % status_text
		return "%s>APRS,TCPIP*:%s" % (callsign, payload)
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
		return "%s>APRS,TCPIP*:%s" % (callsign, payload)
	except:
		return None
