from argparse import ArgumentParser
from jinja2 import Environment, FileSystemLoader
from os import chdir, makedirs
from subprocess import check_call

import grp
import pwd
import os

def chmod(path, mode):
  for root, dirs, files in os.walk(path):
    for dir in dirs:
      os.chmod(os.path.join(root, dir), mode)
    for file in files:
      os.chmod(os.path.join(root, file), mode)
  os.chmod(path, mode)

def chown(path, uid, gid):
  for root, dirs, files in os.walk(path):
    for dir in dirs:
      os.chown(os.path.join(root, dir), uid, gid)
    for file in files:
      os.chown(os.path.join(root, file), uid, gid)
  os.chown(path, uid, gid)

def git_clone(repository = None, destination = None, revision = None):
	command = ['git', 'clone', repository]
	if revision:
		command += ['-b', revision]
	if destination:
		command.append(destination)
	check_call(command)

def install(packages):
	check_call(['apt-get', 'install', '-y'] + packages)

def on_startup(daemon):
	check_call(['update-rc.d', '-f', daemon, 'defaults'])

def run(app, *args):
	check_call([app] + list(args))

def start(service):
	check_call(['service', service, 'start'])

def update_alternatives(app, path):
	check_call(['update-alternatives', '--set', app, path])

def write(template, path):
	with open(path, "wb") as output:
		output.write(template)

if __name__ == "__main__":
	# Parse command line arguments.
	parser = ArgumentParser(description = 'Install the latest stable version of FreeSWITCH from source code ' \
																				'on Ubuntu 12.04.')
	parser.add_argument('--templates', dest = 'templates_path', nargs = '?', required = True, \
											help = 'The absolute path to a folder containing the templates necessary to ' \
														 'install FreeSWITCH.')
	arguments = parser.parse_args()
	# Configure Jinja2.
	loader = FileSystemLoader(arguments.templates_path)
	environment = Environment(loader = loader);
	# Install FreeSWITCH dependencies.
	install(['autoconf', 'automake', 'build-essential', 'gawk', 'git-core', 'libasound2-dev',
					 'libdb-dev', 'libexpat1-dev', 'libcurl4-openssl-dev', 'libgdbm-dev',
					 'libgnutls-dev', 'libjpeg-dev', 'libncurses5', 'libncurses5-dev', 'libperl-dev',
					 'libogg-dev', 'libsnmp-dev', 'libssl-dev', 'libtiff4-dev', 'libtool', 'libvorbis-dev',
					 'libx11-dev', 'libzrtpcpp-dev', 'make', 'python-dev', 'snmp', 'snmp-mibs-downloader',
					 'snmpd', 'subversion', 'unixodbc-dev', 'uuid-dev', 'zlib1g-dev'])
	# Use gawk as the defalt awk interpreter.
	update_alternatives('awk', '/usr/bin/gawk')
	# Start the network management daemon.
	start('snmpd')
	# Fetch the FreeSWITCH source code from Git repository.
	git_clone(repository = 'git://git.freeswitch.org/freeswitch.git', \
			destination = '/usr/src/freeswitch', \
			revision = 'v1.2.stable')
	chdir('/usr/src/freeswitch')
	# Bootstrap the FreeSWITCH build process.
	run('./bootstrap.sh')
	# Configure the FreeSWITCH build environment.
	template = environment.get_template('modules.jinja2')
	modules = template.render()
	write(modules, '/usr/src/freeswitch/modules.conf')
	run('./configure', '--prefix=/usr/share/freeswitch')
	# Build and install FreeSWITCH.
	run('make')
	run('make', 'install')
	run('make', 'uhd-sounds-install')
	run('make', 'uhd-moh-install')
	run('make', 'samples')
	# Sys V Init
	template = environment.get_template('sysvinit.jinja2')
	sysvinit = template.render()
	write(sysvinit, '/etc/init.d/freeswitch')
	chmod('/etc/init.d/freeswitch', 0755)
	on_startup('freeswitch')
	template = environment.get_template('sysvdefault.jinja2')
	sysvdefault = template.render()
	write(sysvdefault, '/etc/default/freeswitch')
	# Add the freeswitch user.
	run('adduser', '--disabled-password', '--system', '--home', '/usr/share/freeswitch', \
  		'--gecos', 'FreeSwitch Voice Platform', '--ingroup', 'daemon', 'freeswitch')
	run('adduser', 'freeswitch', 'audio')
	uid = pwd.getpwnam("freeswitch").pw_uid
	gid = grp.getgrnam("daemon").gr_gid
	# Post install setup.
	chown('/usr/share/freeswitch', uid, gid)
	# Post install configuration.
	template = environment.get_template('modules.conf.xml.jinja2')
	modules = template.render()
	write(modules, '/usr/share/freeswitch/conf/autoload_configs/modules.conf.xml')
	# Finish by starting the newly installed FreeSWITCH server.
	start('freeswitch')

