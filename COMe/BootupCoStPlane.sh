#!/bin/bash

FUN_ROOT="/opt/fungible"
DIR_FUN_CONFIG="/var/opt/fungible/fs1600/configure_bond"

if [[ "$EUID" -ne 0 ]]; then
        printf "Please run as ROOT EUID=$EUID\n"
        exit
fi

echo "Running $0 (`date`)"

SSHPASS=`which sshpass`
if [[ -z $SSHPASS ]]; then
	apt-get install -y sshpass
fi

IPMITOOL=`which ipmitool`
if [[ -z $IPMITOOL ]]; then
	apt-get install -y ipmitool
fi

if [[ ! -f /usr/sbin/in.tftpd ]]; then
	sudo apt-get install -y tftpd-hpa
	# Restrict the tftpserver to serve
	# requests only on the internal interface
	if [[ -f /usr/sbin/in.tftpd ]]; then
		TFTP_SERVER_CONFIG_FILE="/etc/default/tftpd-hpa"
		grep "192" $TFTP_SERVER_CONFIG_FILE > /dev/null 2>&1
		RC=$?
		if [[ $RC -ne 0 ]]; then
			sed -i 's/TFTP_ADDRESS="/TFTP_ADDRESS="192.168.127.4/g' $TFTP_SERVER_CONFIG_FILE
		fi
		grep "create" $TFTP_SERVER_CONFIG_FILE > /dev/null 2>&1
		RC=$?
		if [[ $RC -ne 0 ]]; then
			sed -i 's/secure/-secure --create/g' $TFTP_SERVER_CONFIG_FILE
		fi
	fi
fi

if [[ -f $FUN_ROOT/StorageController/etc/start_splash_screen.sh ]]; then
	$FUN_ROOT/StorageController/etc/start_splash_screen.sh start &
fi

IPMI_LAN="ipmitool -U admin -P admin lan print 1"
AWK_LAN='/IP Address[ ]+:/ {print $4}'
REBOOT_FILE="/tmp/host_reboot"

BMC_IP=$($IPMI_LAN | awk "$AWK_LAN")
printf "Poll BMC:  %s\n" $BMC_IP

BMC="-P password: -p superuser ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no sysadmin@$BMC_IP"

REBOOT=$(sshpass $BMC "ls $REBOOT_FILE" > /dev/null 2>&1)
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

mkdir -p $DIR_FUN_CONFIG
if [[ -f $DIR_FUN_CONFIG/configure_bond ]]; then
	$FUN_ROOT/cclinux/cclinux_service.sh --start --ep --storage --autocreatebond
else
	$FUN_ROOT/cclinux/cclinux_service.sh --start --ep --storage
fi

$FUN_ROOT/StorageController/etc/start_sc.sh start

if [[ -f $FUN_ROOT/etc/DpuHealthMonitor.sh ]]; then
	$FUN_ROOT/etc/DpuHealthMonitor.sh &
fi

#Running DPCSH in TCP-PROXY Mode,
#so that BMC can use this interface
#to fetch F1s' data over NVME interfaces
BMC_F1_0_DPC_PORT=43101
BMC_F1_1_DPC_PORT=43102
BMC_DPCSH_F1_0_LOGF="/var/log/bmc_dpcsh_f1_0.log"
BMC_DPCSH_F1_1_LOGF="/var/log/bmc_dpcsh_f1_1.log"
F1_0_NVME="/dev/nvme0"
F1_1_NVME="/dev/nvme1"

# 10 seconds SWSYS-465
DPCSH_TIMEOUT="10000"

if [[ -f $FUN_ROOT/FunSDK/bin/Linux/dpcsh/dpcsh && -c $F1_0_NVME && -c $F1_1_NVME ]]; then
	$FUN_ROOT/FunSDK/bin/Linux/dpcsh/dpcsh --pcie_nvme_sock=$F1_0_NVME --nvme_cmd_timeout=$DPCSH_TIMEOUT --tcp_proxy=$BMC_F1_0_DPC_PORT > $BMC_DPCSH_F1_0_LOGF 2>&1 &
	$FUN_ROOT/FunSDK/bin/Linux/dpcsh/dpcsh --pcie_nvme_sock=$F1_1_NVME --nvme_cmd_timeout=$DPCSH_TIMEOUT --tcp_proxy=$BMC_F1_1_DPC_PORT > $BMC_DPCSH_F1_1_LOGF 2>&1 &
fi

echo "$0 DONE!!! (`date`)"
