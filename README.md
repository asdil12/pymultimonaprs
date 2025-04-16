> [!WARNING]
> Moved to https://codeberg.org/asdil12/pymultimonaprs

pymultimonaprs
==============

RF2APRS-IG Gateway supporting this backends:

- Pulseaudio
- ALSA
- RTL-SDR


Installation
------------

- Install multimonNG
- Install rtl-sdr (for RTL-SDR backend)
- sudo apt install python3 python3-pkg-resources
- Run `python3 setup.py install`

Configuration
-------------

Edit `/etc/pymultimonaprs.json`:

### Backend

Set the source to `rtl`, `alsa`, or `pulse` to select the backend

### Status

Set the status `text`, or set a status `file` - the content of this file will be read at runtime and sent as status.
This way you can eg. monitor your battery status using APRS-IG.
Set both `text` and `file` to `false` to disable status beacon.

#### Position Ambiguity

To hide your exact position you can set the ambiguity value to a value from 0 to 4.
- 0 will not hide anything
- 1 will decrease precision to 1/10 of a min
- 2 will decrease precision to 1 min
- 3 will decrease precision to 10 min
- 4 will decrease precision to 1°

### Weather

You can set `weather` to a json-file. eg: `"weather": "/path/to/weather.json",`  
If you don't want do send weather date, just leave it on `false`.  
This will be read in like the status-file and can look like that:
```json
{
	"timestamp": 1366148418,
	"wind": {
		"speed": 10,
		"direction": 240,
		"gust": 200
	},
	"temperature": 18.5,
	"rain": {
		"rainlast1h": 10,
		"rainlast24h": 20,
		"rainmidnight": 15
	},
	"humidity": 20,
	"pressure": 1013.25
}
```

#### Legend

- `timestamp` is seconds since epoch - **must** be included
- `wind`
	- `speed` is in km/h
	- `direction` is in deg
	- `gust` is in km/h
- `temperature` is in °C
- `rain`
	- `rainlast1h` is in mm
	- `rainlast24h` is in mm
	- `rainmidnight` is in mm
- `humidity` is in %
- `pressure` is in hPa

The timestamp **must** be included - everything else is optional.

### Symbol

The correct symbol is already selected.
If you still want to change it, you can find the symbol table [here](https://github.com/asdil12/pymultimonaprs/wiki/Symbol-Table).

### IPv4 / IPv6

To select a protocol you can set `preferred_protocol` to `ipv4`, `ipv6` or `any`.  
You use a raw IPv6 address as a gateway like this: `"[2000::1234]:14580"`.

Running
-------

- Run `systemctl start pymultimonaprs` or just `pymultimonaprs -v` for testing
