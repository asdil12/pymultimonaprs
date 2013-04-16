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

Configuration
-------------

Edit `/etc/pymultimonaprs.json`:
- Set the source to `rtl`, `alsa`, or `pulse` to select the backend
- Set the status text, or set a status file - the content of this file will be read at runtime and sent as status.
  This way you can eg. monitor your battery status using APRS-IG

Running
-------

- Run `systemctl start pymultimonaprs` or just `pymultimonaprs` for testing
