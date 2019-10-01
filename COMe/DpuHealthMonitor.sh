#!/bin/bash -e

if [[ "$EUID" -ne 0 ]]; then
        printf "Please run as ROOT EUID=$EUID\n"
        exit
fi

DPU0_HBM_DUMP_COLLECTED="0"
DPU1_HBM_DUMP_COLLECTED="0"
USER_CTRL_C=0

FILE_BLD_NUM="/opt/fungible/bld_props.json"
DIR_HBM_LOGS="/var/log/hbm_dumps"
HBM_FILE_NAME="HBM"
MAX_DUMPS_PER_DPU=3

# Get the build number
if [[ -f $FILE_BLD_NUM ]]; then
	BLD_NUM=`cat $FILE_BLD_NUM | grep bldNum | sed 's/^ *//' | cut -d " " -f 2`
	if [[ -z $BLD_NUM ]]; then
		BLD_NUM="UNKNOWN"
	fi
else
	BLD_NUM="UNKNOWN"
fi

function CleanUpPrevDumps()
{
	DPU_NUM=`echo "D"$1`
	FILE=`echo "$HBM_FILE_NAME"_"$DPU_NUM"`
	mkdir -p $DIR_HBM_LOGS

	NUM_PREV_CORES=`ls $DIR_HBM_LOGS/$FILE* | wc -l`

	if ! [[ $NUM_PREV_CORES -lt $MAX_DUMPS_PER_DPU ]]; then
		# Keep Newest; Delete All
		FILE_LIST=`echo "$DIR_HBM_LOGS"/"$FILE"*`
		ls $FILE_LIST | sort | uniq -u | /usr/bin/head -n -$MAX_DUMPS_PER_DPU | /usr/bin/xargs --no-run-if-empty rm
	fi
}

HBM_BIN="/opt/fungible/bin/hbm_dump_pcie"
START_ADDR="0x100000"
DUMP_MEM_SIZE="0x40000000" # 1GB
DPU_BUS_STR1="/sys/bus/pci/devices/0000:0BUS:00.2/resource2"

function CollectHbmDump()
{
	if [[ $# -ne 2 ]]; then
		echo "Insufficiant args"
		return 1
	fi

	DPU=$1
	if [[ $DPU -ne 0 ]] && [[ $DPU -ne 1 ]]; then
		echo "Incorrect DPU number: $DPU"
		return 1
	fi

	DPU=`echo D$1`
	PCIE_DEV=$2

	SED_STR=`echo s/BUS/"$PCIE_DEV"/`
	DPU_BDF=`echo $DPU_BUS_STR1 | sed $SED_STR`
	# check if above device file exists
	if [[ ! -f $DPU_BDF ]]; then
		echo "Device file $DPU_BDF for DPU $DPU not found"
		return 1
	fi

	DATE=`date +%m-%d-%Y-%H-%M-%S`
	FILE_NAME=`echo "$DIR_HBM_LOGS"/"$HBM_FILE_NAME"_"$DPU"_"$DATE"_BLD"$BLD_NUM".core`

	# This sleep is added because it was observed from
	# FunOS console logs that it takes some time for the
	# backtrace messages to complete whereas the watchdog
	# triggers immediately.
	sleep 30
	echo "$HBM_BIN -a $START_ADDR -s $DUMP_MEM_SIZE -b $DPU_BDF -f -o $FILE_NAME"
	# This commands take 268 secs for 1GB of core dump
	cat /proc/uptime
	$HBM_BIN -a $START_ADDR -s $DUMP_MEM_SIZE -b $DPU_BDF -f -o $FILE_NAME
	cat /proc/uptime
	/bin/gzip -9 $FILE_NAME
}

# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c()
{
        USER_CTRL_C=1
}


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
DPU_STATUS="/tmp/F1_STATUS"
DEST_DIR="/tmp/."

BMC_IP=$($IPMI_LAN | awk "$AWK_LAN")
printf "Poll BMC:  %s\n" $BMC_IP

BMC="-P password: -p superuser scp -o StrictHostKeyChecking=no sysadmin@$BMC_IP:$DPU_STATUS"

# On Failure
#cat /tmp/F1_STATUS
#STATUS: 0x00030000
#F1_0: RUNNING
#F1_1: FAILED

# On Success
#cat /tmp/F1_STATUS
#STATUS: 0x00000000
#F1_0: RUNNING
#F1_1: RUNNING

while true; do

	if [[ $USER_CTRL_C -eq 1 ]]; then
		break
	fi

	# Get the DPU status file from BMC
	DPU_HEALTH=$(sshpass $BMC $DEST_DIR)

	# scan the results
	DPU0_HEALTH=`cat $DPU_STATUS | grep "F1_0" | cut -d " " -f 2`
	DPU1_HEALTH=`cat $DPU_STATUS | grep "F1_1" | cut -d " " -f 2`

	if [[ -z "$DPU0_HEALTH" ]] ||
	   [[ -z "$DPU1_HEALTH" ]]; then
		continue
	fi

	if [[ "$DPU0_HEALTH" == "FAILED" ]] || [[ "$DPU1_HEALTH" == "FAILED" ]]; then
		if [[ "$DPU0_HEALTH" == "FAILED" ]] &&	\
		   [[ "$DPU0_HBM_DUMP_COLLECTED" == "0" ]]; then
			echo "Collecting HBM dump on DPU 0"
			CleanUpPrevDumps 0
			CollectHbmDump 0 4
			DPU0_HBM_DUMP_COLLECTED=1
		fi

		if [[ "$DPU1_HEALTH" == "FAILED" ]] &&	\
		   [[ "$DPU1_HBM_DUMP_COLLECTED" == "0" ]]; then
			echo "Collecting HBM dump on DPU 1"
			CleanUpPrevDumps 1
			CollectHbmDump 1 6
			DPU1_HBM_DUMP_COLLECTED=1
		fi
	fi

	if [[ "$DPU0_HEALTH" == "RUNNING" ]] && [[ "$DPU0_HBM_DUMP_COLLECTED" == "1" ]]; then
		DPU0_HBM_DUMP_COLLECTED=0
	fi

	if [[ "$DPU1_HEALTH" == "RUNNING" ]] && [[ "$DPU1_HBM_DUMP_COLLECTED" == "1" ]]; then
		DPU1_HBM_DUMP_COLLECTED=0
	fi

	rm -f $DPU_STATUS

	# Check every 5 sec
	sleep 5
done

