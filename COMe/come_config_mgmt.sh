#!/bin/bash

# File: come_clean_config.sh
# Created by Jimmy Yeap, updated by David Peet
# Copyright © 2020 Fungible. All rights reserved.
#
# Configures the management stack on F1.
#

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run as ROOT (CurrentEUID=$EUID)"
  exit 1
fi

#
# First, determine the gateway parameters through a combination of
# querying the routing table for 0/0 (the default) and querying
# the arp table.
#
# The routing table query is inexact: the better approach would be to
# query the exact route to the destination through ip route get.
# However, we don't know the destination IP address at this time.
#
GATEWAY_IP=$(ip route show 0/0 | awk '{ print $3 }')
GATEWAY_MAC=$(arp -a ${GATEWAY_IP} | awk '{ print $4 }')

echo "Gateway IP is ${GATEWAY_IP} and MAC is ${GATEWAY_MAC}"

#
# Determine the local IP address: we will use this as F1's management IP
# address as well.
#
INTF=enp3s0f0
MGMT_IP=$(ip -4 addr show ${INTF} | grep inet | awk '{ print $2 }' | cut -d/ -f1)

echo "Management IP is ${MGMT_IP}"

#
# Issue the DPC command to configure management port routing to both
# control plane containers.
#
for N in 0 1
do
  docker ps -f NAME=F1-${N} | grep -q F1-${N}
  if [ ${?} -eq 0 ] ; then
    echo Set for F1-${N}
    echo DO: docker exec -t F1-${N} /opt/fungible/FunSDK/bin/Linux/dpcsh/dpcsh --nocli forwarding_mgmt configure \"${MGMT_IP}\" \"${GATEWAY_MAC}\"
    docker exec -t F1-${N} /opt/fungible/FunSDK/bin/Linux/dpcsh/dpcsh --nocli forwarding_mgmt configure \"${MGMT_IP}\" \"${GATEWAY_MAC}\"
  else
    echo Warning: Not running: F1-${N}
  fi
done
