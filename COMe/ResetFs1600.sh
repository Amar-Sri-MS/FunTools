#!/bin/bash

function Unsupported_Config_Banner()
{
	echo "*************************************************************************"
	echo "*                                                                       *"
	echo "*             INTERNAL TESTING USE ONLY (Usage fine on Rev1/Rev1+)      *"
	echo "*                                                                       *"
	echo "*             THIS MODE WILL NOT WORK AT A CUSTOMER SITE                *"
	echo "*                                                                       *"
	echo "*             INTERNAL TESTING USE ONLY (Usage fine on Rev1/Rev1+)      *" >&2
	echo "*                                                                       *" >&2
	echo "*             THIS MODE WILL NOT WORK AT A CUSTOMER SITE                *" >&2
	echo "*                                                                       *" >&2
	echo "*************************************************************************" >&2
}

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

FUN_ROOT="/opt/fungible"

if [[ "$EUID" -ne 0 ]]; then
	printf "Please run as ROOT EUID=$EUID\n"
	exit
fi

SUSPEND_REBOOT_REQ="/tmp/SuspendCOMeRebootRequests"
if [[ -f $SUSPEND_REBOOT_REQ ]]; then
	printf "Reboot request and is in progress ..."
	exit
fi
# Suspend more reboot requests
touch ${SUSPEND_REBOOT_REQ}

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

# SWSYS-916
# Send a reset request via internal private port to BMC
# If BMC acknowledges the request then exit so that
# BMC can gracefully bring down the COMe
# If the request is not acknowledged then proceed and
# use legacy method
# The legacy method will be required till the time BMC
# gets the chassis bundle which supports this feature
# tracked under SWSYS-916
# This is true for all revisions of FS1600
RETRY=5
while [[ ${RETRY} -ne 0 ]]; do
	#         Reboot request cmd            BMC IP        port
	ACK=`echo RebootRequestFromCOMe | nc -4 192.168.127.2 6672`
	if [[ ! -z "${ACK}" ]] && [[ "${ACK}" == "AckRebootRequestFromCOMe" ]]; then
		echo "Reboot request sent to BMC and ACK received (${ACK})"
		# Keep spinning till BMC reboots COMe
		while true; do
			sync
			sleep 10
		done
	fi
	RETRY=$((RETRY - 1))
	sleep 1
done

# **********************************************************
# * SWSYS-916 (IMPORTANT)                                  *
# * This method of using direct password is depricated     *
# * but is used by Rev1/Rev1+ systems.                     *
# * Do not delete below code+logic as it will brick        *
# * the working model for Rev1/Rev1+ and Rev2 systems      *
# * which do not have corrosponding chassis bundle support *
# **********************************************************
echo "Using legacy method to issue system reboot request to BMC"

Unsupported_Config_Banner

FAST_REBOOT=0
if [[ $# -eq 1 ]]; then
	ARG=$1
	if [[ $ARG == "-f" ]] || [[ $ARG == "--fast" ]]; then
		FAST_REBOOT=1
	else
		printf "Unsupported option %s\n" $ARG
	fi
fi

REBOOT_FILE="/tmp/fpga_reset.sh"

if [[ -d /sys/class/net/enp3s0f0.2 ]]; then
	BMC_IP="192.168.127.2"
else
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
# **********************************************************
# * SWSYS-916 (IMPORTANT)                                  *
# * This method of using direct password is depricated     *
# * but is used by Rev1/Rev1+ systems.                     *
# * Do not delete below code+logic as it will brick        *
# * the working model for Rev1/Rev1+ and Rev2 systems      *
# * which do not have corrosponding chassis bundle support *
# **********************************************************
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

