#!/bin/bash -e

NOBOOT="/tmp/NoCOMeReboot.sh"

if [[ "$EUID" -ne 0 ]]; then
	printf "Please run as ROOT EUID=$EUID\n"
	exit
fi

echo "Running $0"

if [[ -f $NOBOOT ]]; then
	printf "Aborting reboot request"
	printf "Please remove file $NOBOOT"
fi

exit

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

BMC="-P password: -p superuser ssh -o StrictHostKeyChecking=no sysadmin@$BMC_IP"

printf "WARNING: Sending BMC request to reboot host\n"
printf "\n**********************************************\n"
printf "\n!!! Hold on to the bars, we are going down !!!\n"
printf "\n**********************************************\n"

COUNT=0
while [[ $COUNT -lt 120 ]]; do
	REBOOT=$(sshpass $BMC "exec $REBOOT_FILE")
        sleep 1
        let COUNT=COUNT+1
done

# Should never reach here
printf "!!! COMe was not able to send reset request to BMC !!!"
