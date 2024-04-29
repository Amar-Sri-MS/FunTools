#!/usr/bin/env bash

# script to backup the signing/enrollment/boot_step server
# Copyright 2023 Microsoft Corporation. All Rights Reserved.

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root."
    exit 1
fi


mkdir -p /media/install

# archiving the files:
tar -v -c -z -f /media/install/install.tgz \
    /etc/httpd/conf.d/http2https.conf \
    /etc/httpd/conf.d/enrollment.conf \
    /etc/httpd/conf.d/signing.conf \
    /etc/pki/tls/certs/fungible.com.pem \
    /etc/pki/tls/certs/fungible.com.ca-chain.pem \
    /etc/pki/tls/certs/DPUProductionSigning.pem \
    /etc/pki/tls/private/fungible.com.key.pem \
    /usr/lib/cgi-bin \
    /var/lib/dpu_reg \
    /var/www/api \
    /var/www/html

# PostgresQL dump
sudo -u dpureg pg_dump -d enrollment_db > /media/install/enrollment_db.sql
