#!/usr/bin/env python2

from distutils.core import setup
from distutils.command.install import install
from distutils.dir_util import mkpath
import pkg_resources
import os
import sys
import shutil

class post_install(install):
	def run(self):
		prefix = getattr(self, "install_data", "/") or "/"
		root = getattr(self, "root", "/") or "/"
		print "Using '%s' as root" % root
		if root == "/":
			if os.getuid() != 0:
				print "ERROR: Can't install to root '/' without root permissions"
				sys.exit(1)
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
		if root == "/":
			# fix prefix in systemd.service file
			unitfile = os.path.join(root, "/usr/lib/systemd/system", "pymultimonaprs.service")
			print unitfile
			new_content = open(unitfile).read().replace("/usr/bin", "%s/bin" % prefix)
			open(unitfile, "w").write(new_content)
		# install config file
		print ""
		cd = os.path.dirname(os.path.realpath(__file__))
		src = os.path.join(cd, "pymultimonaprs.json")
		dest = os.path.join(root, "etc/pymultimonaprs.json")
		dest_new = os.path.join(root, "etc/pymultimonaprs.json.new")
		mkpath(os.path.dirname(dest))
		if os.path.isfile(dest):
			print "Warning: %s already exists! Saved new config file to %s" % (dest, dest_new)
			shutil.copyfile(src, dest_new)
		else:
			print "Installing config file to %s" % dest
			shutil.copyfile(src, dest)



setup(
	name='pymultimonaprs',
	version='1.3.1',
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
