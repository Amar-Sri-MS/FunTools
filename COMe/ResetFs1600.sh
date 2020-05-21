#!/bin/bash -e

echo "*************************************************************************"
echo "*                                                                       *"
echo "*             INTERNAL TESTING USE ONLY                                 *"
echo "*                                                                       *"
echo "*             THIS SCRIPT WILL NOT WORK AT A CUSTOMER SITE              *"
sleep 2
echo "*                                                                       *"
echo "*             THIS SCRIPT IS DEPRICATED                                 *"
echo "*                                                                       *"
echo "*             PLEASE USE THE BMC CLI TO RESET COMe (cclinux)            *"
echo "*             CLI: fun_reboot_system.sh                                 *"
sleep 3
echo "*                                                                       *"
echo "*             THIS SCRIPT WILL NOT WORK AT A CUSTOMER SITE              *" >&2
echo "*                                                                       *" >&2
echo "*             INTERNAL TESTING USE ONLY                                 *" >&2
echo "*                                                                       *" >&2
echo "*************************************************************************" >&2
sleep 5

# SWSYS-740
# Poll the operational state of the interface for
# 10 seconds to check if the interface is 'up'
function Is_Interface_Up()
{
	INTF=$1
	COUNT=10
	while [[ $COUNT -ne 0 ]]; do
		INTF_OPER_ST=`cat $INTF/operstate` > /dev/null 2>&1
		if [[ $INTF_OPER_ST == "up" ]]; then
			echo "Interface ($INTF) is up"
			return 0;
		fi

		COUNT=$((COUNT - 1))
		sleep 1
	done

	echo "Interface ($INTF) is down"

	return 1
}

NOREBOOT="/tmp/SuspendCOMeRebootRequests"
FUN_ROOT="/opt/fungible"

if [[ "$EUID" -ne 0 ]]; then
	printf "Please run as ROOT EUID=$EUID\n"
	exit
fi

echo "Running $0"

#SWSYS-604
INTERNAL_VLAN_VIRT_INTF="/sys/class/net/enp3s0f0.2"
Is_Interface_Up $INTERNAL_VLAN_VIRT_INTF
RC=$?
if [[ $RC -ne 0 ]]; then
	echo "Interface $INTERNAL_VLAN_VIRT_INTF is in down state"
	netplan apply
	# check once more if the interface is up
	Is_Interface_Up $INTERNAL_VLAN_VIRT_INTF
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
        echo ERROR: sshpass is not installed!!!!!!!!!!
	apt-get install -y sshpass
fi

REBOOT_FILE="/tmp/fpga_reset.sh"

if [[ -d /sys/class/net/enp3s0f0.2 ]]; then
	BMC_IP="192.168.127.2"
else
        IPMITOOL=`which ipmitool`
        if [[ -z $IPMITOOL ]]; then
                echo ERROR: ipmitool is not installed!!!!!!!!!!
	        apt-get install -y ipmitool
        fi
	IPMI_LAN="ipmitool lan print 1"
	AWK_LAN='/IP Address[ ]+:/ {print $4}'
	BMC_IP=$($IPMI_LAN | awk "$AWK_LAN")
fi

printf "Poll BMC:  %s\n" $BMC_IP

BMC="-P password: -p superuser ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no sysadmin@$BMC_IP"

# Save unfinished work in FS before async reboot
sync

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

