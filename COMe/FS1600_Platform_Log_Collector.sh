#!/bin/bash -e

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

/bin/cp $HBM_DUMP_FILES_PREFIX $LOG_STASH

# ***********************************
# * Copy the platform boot-up files *
# ***********************************

COMe_BOOT_UP_DIR="/var/log"
COMe_BOOT_UP_FILE=`echo "$COMe_BOOT_UP_DIR"/fs1600-come-boot-up.log`
COMe_BOOT_UP_ARCHIVE_FILE_PREFIX=`echo "$COMe_BOOT_UP_DIR"/FS1600_*`

/bin/cp $COMe_BOOT_UP_FILE $LOG_STASH
/bin/cp $COMe_BOOT_UP_ARCHIVE_FILE_PREFIX $LOG_STASH

# ***************************
# * Get FunOs logs from BMC *
# ***************************

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
FUNOS_LOGS="/mnt/sdmmc0p1/log/*"

BMC_IP=$($IPMI_LAN | awk "$AWK_LAN")

BMC="-P password: -p superuser scp -o StrictHostKeyChecking=no sysadmin@$BMC_IP:$FUNOS_LOGS"

$SSHPASS $BMC $LOG_STASH

echo "Finished collecting logs to stash $LOG_STASH (Date: `date`)"

