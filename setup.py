#!/usr/bin/env python2

from distutils.core import setup
from distutils.command.install import install
import pkg_resources
import os
import shutil

class post_install(install):
	def run(self):
		# cleanup old egg-info files
		try:
			while True:
				p = pkg_resources.get_distribution("pymultimonaprs")
				for f in os.listdir(p.location):
					if f.startswith("pymultimonaprs") and f.endswith(".egg-info"):
						egg_info = os.path.join(p.location, f)
						try:
							print "Deleting old egg-info: %s" % egg_info
							os.unlink(egg_info)
						except:
							pass
				reload(pkg_resources)
		except pkg_resources.DistributionNotFound:
			pass
		install.run(self)
		# install config file
		print ""
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
