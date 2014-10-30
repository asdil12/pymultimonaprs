#!/usr/bin/env python2

from distutils.core import setup

setup(
	name='pymultimonaprs',
	version='1.0.0',
	license='GPL',
	description='RF2APRS-IG Gateway',
	author='Dominik Heidler',
	author_email='dominik@heidler.eu',
	url='http://github.com/asdil12/pymultimonaprs',
	packages=['pymultimonaprs'],
	scripts=['bin/pymultimonaprs'],
	data_files=[
		('/etc', ['pymultimonaprs.json']),
		('/usr/lib/systemd/system', ['pymultimonaprs.service']),
	],
)
