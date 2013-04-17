#!/usr/bin/env python2

from distutils.core import setup

setup(
	name='pymultimonaprs',
	version='0.7',
	license='GPL',
	description='HF2APRS-IG Gateway',
	author='Dominik Heidler',
	author_email='dheidler@gmail.com',
	url='http://github.com/asdil12/pymultimonaprs',
	packages=['pymultimonaprs'],
	scripts=['bin/pymultimonaprs'],
	data_files=[
		('/etc', ['pymultimonaprs.json']),
		('/usr/lib/systemd/system', ['pymultimonaprs.service']),
	],
)
