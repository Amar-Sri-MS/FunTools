#!/bin/bash -e

NOREBOOT="/tmp/SuspendCOMeRebootRequests"
FUN_ROOT="/opt/fungible"

if [[ "$EUID" -ne 0 ]]; then
	printf "Please run as ROOT EUID=$EUID\n"
	exit
fi

echo "Running $0"

#SWSYS-604
INTERNAL_VLAN_VIRT_INTF="/sys/class/net/enp3s0f0.2"
if [[ -d $INTERNAL_VLAN_VIRT_INTF/operstate ]]; then
        UP_STATE=`cat $INTERNAL_VLAN_VIRT_INTF/operstate`
        if [[ $UP_STATE == "down" ]]; then
                echo "Interface $INTERNAL_VLAN_VIRT_INTF is in down state"
                netplan apply
        fi
fi

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

REBOOT_FILE="/tmp/fpga_reset.sh"

if [[ -d /sys/class/net/enp3s0f0.2 ]]; then
	BMC_IP="192.168.127.2"
else
	IPMI_LAN="ipmitool -U admin -P admin lan print 1"
	AWK_LAN='/IP Address[ ]+:/ {print $4}'
	BMC_IP=$($IPMI_LAN | awk "$AWK_LAN")
fi

printf "Poll BMC:  %s\n" $BMC_IP

BMC="-P password: -p superuser ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no sysadmin@$BMC_IP"

# Save unfinished work in FS before async reboot
sync

if [[ -f $FUN_ROOT/StorageController/etc/start_sc.sh ]]; then
	printf "Shutdown the storage controller\n"
	$FUN_ROOT/StorageController/etc/start_sc.sh stop
	sync
fi

# This is a blocking call -> Eddie
$FUN_ROOT/cclinux/cclinux_service.sh --stop
sync

# Save unfinished work in FS before async reboot
sync

printf "\n**********************************************\n"
printf "\n!!! Hold on to the bars, we are going down !!!\n"
printf "\n**********************************************\n"

if [[ $FAST_REBOOT -eq 1 ]]; then
	printf "Triggering fast reboot\n"
	/sbin/reboot
else
	# Generate a simple script which will initiate
	# reset sequence on the script
	# This script is push to BMC and then executed
	# in background on BMC
	RESET_CONTROLLER="/tmp/FS1600_Reset_Controller.sh"
	touch $RESET_CONTROLLER
	echo "#!/bin/sh" > $RESET_CONTROLLER
	echo "sleep 20" >> $RESET_CONTROLLER
	echo "exec $REBOOT_FILE" >> $RESET_CONTROLLER
	chmod 777 $RESET_CONTROLLER
	# --- Script generated ---

	printf "WARNING: Sending BMC request to reboot host\n"
	COUNT=0
	while [[ $COUNT -lt 1 ]]; do
		BMC_XFER_RST_CTRL="-P password: -p superuser scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $RESET_CONTROLLER sysadmin@$BMC_IP:/tmp"
		echo "Transferring reset controller to BMC"
		XFER=$(sshpass $BMC_XFER_RST_CTRL > /dev/null 2>&1)
		echo "Transfer complete"
		echo "Executing reset controller"
		#CMD="( ( nohup $RESET_CONTROLLER &> /dev/null ) & )"
		REBOOT=$(sshpass $BMC "exec $RESET_CONTROLLER > /dev/null 2>&1 &")
		echo "Execution done"
		/sbin/shutdown -h now
		sleep 60
		let COUNT=COUNT+1
	done

	# Should never reach here
	printf "!!! COMe was not able to send reset request to BMC !!!"
fi

