#!/bin/bash -e

echo "*************************************************************************"
echo "*                                                                       *"
echo "*             INTERNAL TESTING USE ONLY                                 *"
echo "*                                                                       *"
echo "*             THIS SCRIPT WILL NOT WORK AT A CUSTOMER SITE              *"
echo "*                                                                       *"
sleep 5
echo "*             THIS SCRIPT WILL NOT WORK AT A CUSTOMER SITE              *" >&2
echo "*                                                                       *" >&2
echo "*             INTERNAL TESTING USE ONLY                                 *" >&2
echo "*                                                                       *" >&2
echo "*************************************************************************" >&2
sleep 5

if [[ "$EUID" -ne 0 ]]; then
        printf "Please run as ROOT EUID=$EUID\n"
        exit
fi

if [[ $# -ne 1 ]]; then
	echo "Incomplete arguments"
	exit 1
fi

LOG_STASH=$1

if [[ ! -d $LOG_STASH ]]; then
	echo "Log stash directory not found"
	exit 1
fi

echo "Start collecting logs to stash $LOG_STASH (Date: `date`)"


# **********************
# * Copy the HBM files *
# **********************

HBM_DUMP_DIR="/var/log/hbm_dumps"
HBM_DUMP_FILES_PREFIX=`echo "$HBM_DUMP_DIR"/HBM_D*`

if [[ -d $HBM_DUMP_DIR ]]; then
	# Check if atlest one file with that prefix exits
	if ls $HBM_DUMP_FILES_PREFIX 1> /dev/null 2>&1; then
		/bin/cp $HBM_DUMP_FILES_PREFIX $LOG_STASH
	fi
fi

# ***********************************
# * Copy the platform boot-up files *
# ***********************************

COMe_BOOT_UP_DIR="/var/log"
COMe_BOOT_UP_FILE=`echo "$COMe_BOOT_UP_DIR"/COMe-boot-up.log`
COMe_BOOT_UP_ARCHIVE_FILE_PREFIX=`echo "$COMe_BOOT_UP_DIR"/FS1600_*`

if [[ -d $COMe_BOOT_UP_DIR ]]; then
	# Check if atlest one file with that prefix exits
	if ls $COMe_BOOT_UP_ARCHIVE_FILE_PREFIX 1> /dev/null 2>&1; then
		/bin/cp $COMe_BOOT_UP_FILE $LOG_STASH
		/bin/cp $COMe_BOOT_UP_ARCHIVE_FILE_PREFIX $LOG_STASH
	fi
fi

# ***************************
# * Get FunOs logs from BMC *
# ***************************

SSHPASS=`which sshpass`
if [[ -z $SSHPASS ]]; then
        echo ERROR: sshpass is not installed!!!!!!!!!!
        apt-get install -y sshpass
fi

FUNOS_LOGS="/mnt/sdmmc0p1/log/*"
if [[ -d /sys/class/net/enp3s0f0.2 ]]; then
        BMC_IP="192.168.127.2"
else
	IPMI_LAN="ipmitool lan print 1"
	AWK_LAN='/IP Address[ ]+:/ {print $4}'
	BMC_IP=$($IPMI_LAN | awk "$AWK_LAN")
fi

printf "Poll BMC:  %s\n" $BMC_IP

BMC="-P password: -p superuser scp -o StrictHostKeyChecking=no sysadmin@$BMC_IP:$FUNOS_LOGS"

$SSHPASS $BMC $LOG_STASH

echo "Finished collecting logs to stash $LOG_STASH (Date: `date`)"

