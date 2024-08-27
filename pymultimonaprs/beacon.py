#!/usr/bin/python3

import os
import json
from datetime import datetime
from pymultimonaprs.frame import APRSFrame

def process_ambiguity(pos, ambiguity):
    num = list(pos)  # Converting to a list for string manipulation
    for i in range(0, ambiguity):
        if i > 1:
            # skip the dot
            i += 1
        # skip the direction
        i += 2
        num[-i] = " "
    return ''.join(num)

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
    frame.dest = 'APPM13'
    frame.path = ['TCPIP*']
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
        if status.get('file') and os.path.exists(status['file']):
            with open(status['file'], 'r', encoding='utf-8') as file:
                status_text = file.read().strip()
        elif status.get('text'):
            status_text = status['text']
        else:
            return None
        payload = ">%s" % status_text
        return mkframe(callsign, payload)
    except Exception as e:
        print(f"Error in get_status_frame: {e}")
        return None

def get_weather_frame(callsign, weather):
    try:
        with open(weather, 'r', encoding='utf-8') as file:
            w = json.load(file)

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
            wenc += "t%03d" % round(w['temperature'] / (5/9) + 32)
        else:
            wenc += "t..."

        # Rain
        rain = w.get('rain', {})
        if 'rainlast1h' in rain:
            si = round((rain['rainlast1h'] / 25.4) * 100)
            wenc += "r%03d" % si
        else:
            wenc += "r..."
        if 'rainlast24h' in rain:
            si = round((rain['rainlast24h'] / 25.4) * 100)
            wenc += "p%03d" % si
        else:
            wenc += "p..."
        if 'rainmidnight' in rain:
            si = round((rain['rainmidnight'] / 25.4) * 100)
            wenc += "P%03d" % si
        else:
            wenc += "P..."

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
    except Exception as e:
        print(f"Error in get_weather_frame: {e}")
        return None
