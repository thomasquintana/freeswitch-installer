freeswitch-installer
====================

Installs FreeSWITCH 1.2.stable on Ubuntu 12.xx releases.

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
