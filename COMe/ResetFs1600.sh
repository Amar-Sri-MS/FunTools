#!/bin/bash -e

NOREBOOT="/tmp/SuspendCOMeRebootRequests"
FUN_ROOT="/opt/fungible"

if [[ "$EUID" -ne 0 ]]; then
	printf "Please run as ROOT EUID=$EUID\n"
	exit
fi

echo "Running $0"

if [[ -f $NOREBOOT ]]; then
	printf "Aborting reboot request"
	printf "Please remove file $NOREBOOT"
	exit
fi

FAST_REBOOT=0
if [[ $# -eq 1 ]]; then
	ARG=$1
	if [[ $ARG == "-f" ]] || [[ $ARG == "--fast" ]]; then
		FAST_REBOOT=1
	else
		printf "Unsupported option %s\n" $ARG
	fi
fi

SSHPASS=`which sshpass`
if [[ -z $SSHPASS ]]; then
	apt-get install -y sshpass
fi

IPMITOOL=`which ipmitool`
if [[ -z $IPMITOOL ]]; then
	apt-get install -y ipmitool
fi

IPMI_LAN="ipmitool -U admin -P admin lan print 1"
AWK_LAN='/IP Address[ ]+:/ {print $4}'
REBOOT_FILE="/tmp/fpga_reset.sh"

BMC_IP=$($IPMI_LAN | awk "$AWK_LAN")
printf "Poll BMC:  %s\n" $BMC_IP

BMC="-P password: -p superuser ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no sysadmin@$BMC_IP"

# Save unfinished work in FS before async reboot
sync

printf "Shutdown the storage controller\n"
$FUN_ROOT/StorageController/etc/start_sc.sh stop

# Save unfinished work in FS before async reboot
sync

printf "\n**********************************************\n"
printf "\n!!! Hold on to the bars, we are going down !!!\n"
printf "\n**********************************************\n"

if [[ $FAST_REBOOT -eq 1 ]]; then
	printf "Triggering fast reboot\n"
	/sbin/reboot
else
	printf "WARNING: Sending BMC request to reboot host\n"
	COUNT=0
	while [[ $COUNT -lt 120 ]]; do
		REBOOT=$(sshpass $BMC "exec $REBOOT_FILE" > /dev/null 2>&1)
		sleep 1
		let COUNT=COUNT+1
	done

	# Should never reach here
	printf "!!! COMe was not able to send reset request to BMC !!!"
fi

