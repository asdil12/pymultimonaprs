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
- Run `python2 setup.py install`
- Edit `/etc/pymultimonaprs.json`:
	- Set the source to `rtl`, `alsa`, or `pulse` to select the backend
- Run `systemctl start pymultimonaprs` or just `pymultimonaprs` for testing
