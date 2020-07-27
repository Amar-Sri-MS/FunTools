#!/bin/bash
#
# File: update_ubuntu.sh
# Created by David Peet (david.peet@fungible.com)
# Copyright © 2020 Fungible. All rights reserved.
#
# Must be run by root.
# Update netplan to these packages:
P1=/opt/fungible/third_party/ubuntu/libnetplan0_0.99-0ubuntu3~18.04.3_amd64.deb
P2=/opt/fungible/third_party/ubuntu/netplan.io_0.99-0ubuntu3~18.04.3_amd64.deb

if [ ! -f ${P1} -o ! -f ${P2} ] ; then
  echo Error, need these files:
  echo ${P1}
  echo ${P2}
fi

CURRENT_V=$(dpkg -l netplan.io | tail -1 | awk '{print $3}')
echo Current netplan.io version: ${CURRENT_V}
CV=$(echo ${CURRENT_V} | cut -f1 -d-)
[ "${CV}" == "0.99" ] && exit 0  # Already installed, so just exit

C1=$(echo ${CV} | cut -f1 -d.)  # first number
C2=$(echo ${CV} | cut -f2 -d.)  # second number
[ ${C1} -gt  0 ] && exit 0  # Current has higher version, so just exit
[ ${C2} -gt 99 ] && exit 0  # Current has higher version, so just exit

echo Updating netplan to version 0.99-0ubuntu3~18.04.3 from version ${CV}
dpkg -i ${P1} ${P2}
exit 0
