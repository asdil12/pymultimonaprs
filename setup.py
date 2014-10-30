#!/usr/bin/env python2

from distutils.core import setup
from distutils.command.install import install

class post_install(install):
	def run(self):
		install.run(self)
		# install config file
		print ""
		import os
		import shutil
		cd = os.path.dirname(os.path.realpath(__file__))
		src = os.path.join(cd, "pymultimonaprs.json")
		if os.path.isfile("/etc/pymultimonaprs.json"):
			print "Warning: /etc/pymultimonaprs.json already exists! Saved new config file to /etc/pymultimonaprs.json.new"
			shutil.copyfile(src, "/etc/pymultimonaprs.json.new")
		else:
			print "Installing config file to /etc/pymultimonaprs.json"
			shutil.copyfile(src, "/etc/pymultimonaprs.json")



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
		#('/etc', ['pymultimonaprs.json']),
		('/usr/lib/systemd/system', ['pymultimonaprs.service']),
	],
	cmdclass={'install': post_install},
)
