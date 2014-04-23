freeswitch-installer
====================

Installs FreeSWITCH 1.2.stable on Ubuntu.

Install Dependencies
====================
```
$] sudo apt-get install -y python-pip
$] sudo pip install Jinja2
```

Usage
=====

```
$] git clone https://github.com/thomasquintana/freeswitch-installer.git
$] cd freeswitch-installer
$] sudo python ./install-freeswitch.py --templates /home/ubuntu/freeswitch-installer/templates
```
It's important to note that the path to templates is absolute and not relative!

Notes
=====

The installer tries to install the snmp-mibs-downloader which is in the multiverse repository. If you are planning on running this script on Amazon's EC2 service make sure to enable the multiverse repostiory and run sudo apt-get update first.
