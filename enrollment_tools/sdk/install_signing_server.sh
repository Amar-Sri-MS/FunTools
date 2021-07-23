#!/usr/bin/env bash
#
# Simple Signing Server Installation for Fungible SDK
#
# Copyright (c) 2021. Fungible, Inc.
# All rights reserved.


if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root."
    exit 1
fi


# install apache
apt install apache2
# enable cgi
a2enmod cgid
# install script and key files (optional argument for tar.gz file)
tar -xzvf ${1:-signing_server.tar.gz}  -C /usr/lib/cgi-bin
# restart apache
systemctl restart apache2
# test using localhost
wget -O -  'http://localhost/cgi-bin/signing_server.cgi?cmd=modulus&key=hkey1&format=c_struct'
