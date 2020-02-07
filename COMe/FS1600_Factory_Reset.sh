#!/bin/bash
#
# File: FS1600_Factory_Reset.sh
# Created by David Peet (david.peet@fungible.com)
# Copyright © 2020 Fungible. All rights reserved.
#
# Return the FS1600 COMEe to 'factory' state ready to
# install a new software version.
# 1. Make sure the services are stopped.
#    Storage Controller and CC Linux service
# 2. Unload funeth driver
# 3. Move logs to save location. 

FUNGIBLE_ROOT=${FUNGIBLE_ROOT:-/opt/fungible}

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run as ROOT (CurrentEUID=$EUID)"
  exit 1
fi

#############################################################
# Step 1. Make sure the services are stopped.
# Stop StorageController service
if [ ! -f ${FUNGIBLE_ROOT}/StorageController/etc/start_sc.sh ] ; then
  echo StorageController not installed.
else
  echo Stopping Storage Controller
  ${FUNGIBLE_ROOT}/StorageController/etc/start_sc.sh stop
  ${FUNGIBLE_ROOT}/StorageController/etc/start_sc.sh -c
fi
# Stop CCLinux service
if [ ! -f ${FUNGIBLE_ROOT}/cclinux/cclinux_service.sh ] ; then
  echo cclinux not installed
else
  echo Stopping cclinux service
  ${FUNGIBLE_ROOT}/cclinux/cclinux_service.sh --stop
fi

#############################################################
# Step 2. Unload drivers
echo Unload drivers TBD
CNT=$(echo $(lsmod | grep funeth | wc -l))
if [ ${CNT} -ne 0 ] ; then
  echo Remove funeth driver
  rmmod funeth
fi

#############################################################
# Step 3. Move logs to save location.
echo Save logs in /var/log/prev
[ ! -d /var/log/prev ] && mkdir /var/log/prev
chmod 755 /var/log/prev
for DIR in fungible sc
do
  [ ! -d /var/log/${DIR} ] && continue
  if [ -d /var/log/prev/${DIR} ] ; then
    rm -rf /var/log/prev/${DIR}
  else
    mv /var/log/${DIR} /var/log/prev/
  fi
done
for FILE in /var/log/FS1600* /var/log/COMe* /var/log/bmc*
do
  [ -f ${FILE} ] && mv ${FILE} /var/log/prev/
done

echo Done
