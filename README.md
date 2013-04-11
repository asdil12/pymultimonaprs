pymultimonaprs
==============

HF2APRS-IG Gateway supporting this backends:

- Pulseaudio
- ALSA
- RTL-SDR


Installation
------------

- Install multimonNG
- Install rtl-sdr (for RTL-SDR backend)
- Copy config.json.sample to config.json and edit it:
	- Set the source to `rtl`, `alsa`, or `pulse` to select the backend
- Run ./pymultimonaprs.py
