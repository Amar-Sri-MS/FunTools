#!/bin/bash

FUN_ROOT="/opt/fungible"

if [[ "$EUID" -ne 0 ]]; then
        printf "Please run as ROOT EUID=$EUID\n"
        exit
fi

echo "Running $0"

SSHPASS=`which sshpass`
if [[ -z $SSHPASS ]]; then
	apt-get install -y sshpass
fi

IPMITOOL=`which ipmitool`
if [[ -z $IPMITOOL ]]; then
	apt-get install -y ipmitool
fi

if [[ -f $FUN_ROOT/StorageController/etc/start_splash_screen.sh ]]; then
	$FUN_ROOT/StorageController/etc/start_splash_screen.sh start &
fi

IPMI_LAN="ipmitool -U admin -P admin lan print 1"
AWK_LAN='/IP Address[ ]+:/ {print $4}'
REBOOT_FILE="/tmp/host_reboot"

BMC_IP=$($IPMI_LAN | awk "$AWK_LAN")
printf "Poll BMC:  %s\n" $BMC_IP

BMC="-P password: -p superuser ssh -o StrictHostKeyChecking=no sysadmin@$BMC_IP"

REBOOT=$(sshpass $BMC "ls $REBOOT_FILE")
if [ "$REBOOT" = "$REBOOT_FILE" ]; then
    printf "WARNING: BMC request to reboot host\n"
    sshpass $BMC "rm $REBOOT_FILE"
    reboot
else
	echo "Reboot from BMC not required. Continuing..."
fi

echo "Init CoSt Plane!!!"

# Hot-plug not supported so no need to wait if F1 are not see upon boot-up
BDFID=`lspci -d 1dad: | grep "Ethernet controller" | cut -d " " -f 1`
if [[ -z "$BDFID" ]]; then
	echo "F1 EP not found"
	exit 1
fi

# Find out how many F1's are available log for debugging
F1COUNT=`lspci -d 1dad: | grep "Ethernet controller" | cut -d " " -f 1 | wc -l`
echo "$F1COUNT F1 found"

export USER="fun"
export HOME="/home/fun"

$FUN_ROOT/cclinux/cclinux_service.sh --start --ep --storage
$FUN_ROOT/StorageController/etc/start_sc.sh start

if [[ -f $FUN_ROOT/etc/DpuHealthMonitor.sh ]]; then
	$FUN_ROOT/etc/DpuHealthMonitor.sh &
fi

echo "$0 DONE!!!"
