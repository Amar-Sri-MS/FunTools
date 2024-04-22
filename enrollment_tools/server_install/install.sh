#!/usr/bin/env bash

# script to setup the signing/enrollment/boot_step server
# Copyright 2023 Microsoft Corporation. All Rights Reserved.

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root."
    exit 1
fi

##### DNF and Python packages installation

########## DNF
# install a few things, selecting non obsolete packages instead of the default
# ones that are still used by RHEL 8.8 (python, PostgresQL)

dnf -y install python39 python39-devel python39-pip python39-setuptools
dnf -y install httpd mod_ssl
dnf -y install postgresql:15/server

# still installing 1.1.1k
dnf -y install openssl openssl-libs

### RPM: OpenSSL ESRP engine
rpm -i esrpengine-1.2-2.x86_64.rpm
ln -s /opt/esrpengine/libesrpEngine.so /usr/lib64/engines-1.1/esrp.so

########## python3.9 packages
python3.9 -m pip install cryptography requests asn1crypto

#special since it might fail if some things were missed earlier
python3.9 -m pip install psycopg2

### Extract all the file to their new places with correct owners
tar xzvf install.tgz -C /

########### PostgresQL setup
# create dpureg user as owner of database
useradd -d '/' -c 'enrollment_db owner' dpureg

# grant dpureg superuser status for postgresql
sudo -u postgres createuser -s dpureg
# grant apache user access to postgresql
sudo -u postgres createuser apache

# transport the pg_dump'ed database
sudo -u postgres psql -f enrollment_db.sql

########### Enable and Start HTTPD service
systemctl enable httpd
systemctl start  httpd
