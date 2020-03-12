#!/bin/bash -e

if [[ "$EUID" -ne 0 ]]; then
        printf "Please run as ROOT EUID=$EUID\n"
        exit
fi

LOOP_INTERVAL=5
DPU0_HBM_DUMP_COLLECTED=0
DPU1_HBM_DUMP_COLLECTED=0
USER_CTRL_C=0
FS1600_RESET="/opt/fungible/etc/ResetFs1600.sh"
NO_CONTINUOUS_REBOOT_TIME_MARK=1200
CONTINUOUS_REBOOT_COUNTER="/var/log/fs1600_reboot_counter"
STOP_REBOOTS=0
MAX_CONTINUOUS_REBOOTS=3

FILE_BLD_NUM="/opt/fungible/.version"
DIR_HBM_LOGS="/var/log/hbm_dumps"
HBM_FILE_NAME="HBM"
MAX_DUMPS_PER_DPU=3

# Get the build number
if [[ -f $FILE_BLD_NUM ]]; then
	BLD_NUM=`cat $FILE_BLD_NUM | grep fs1600 | cut -d "=" -f 2`
	if [[ -z $BLD_NUM ]]; then
		BLD_NUM="UNKNOWN"
	fi
else
	BLD_NUM="UNKNOWN"
fi

function DetectDpuPcieBus()
{
	for i in `lspci -d 1dad: | grep "Ethernet controller" | cut -d " " -f 1`; do
		PHY_SLOT=`lspci -vvv -s $i | grep "Physical Slot" | cut -d ":" -f 2 | sed 's/^ //'`

		if [[ "$PHY_SLOT" == "1" ]]; then
			DPU_0_PCIE_BUS=`echo $i | cut -d ":" -f 1`
		elif [[ "$PHY_SLOT" == "0-"* ]]; then
			DPU_1_PCIE_BUS=`echo $i | cut -d ":" -f 1`
		fi
	done

	echo "DPU_0_PCIE_BUS=$DPU_0_PCIE_BUS"
	echo "DPU_1_PCIE_BUS=$DPU_1_PCIE_BUS"
}


function CleanUpPrevDumps()
{
	DPU_NUM=`echo "D"$1`
	FILE=`echo "$HBM_FILE_NAME"_"$DPU_NUM"`
	mkdir -p $DIR_HBM_LOGS

	# Delete all incomplete files
	# This can happen if user is impatient and
	# reboot the system before HBM dump cpmpletes
	ls `echo $DIR_HBM_LOGS/*` | grep $FILE | grep -v `echo $FILE.*.bz2` | /usr/bin/xargs --no-run-if-empty rm

	NUM_PREV_CORES=`ls $DIR_HBM_LOGS/$FILE* 2>/dev/null 2>&1 | wc -l`

	if ! [[ $NUM_PREV_CORES -lt $MAX_DUMPS_PER_DPU ]]; then
		# Keep Newest; Delete All
		FILE_LIST=`echo "$DIR_HBM_LOGS"/"$FILE"*`
		ls $FILE_LIST | sort | uniq -u | /usr/bin/head -n -$MAX_DUMPS_PER_DPU | /usr/bin/xargs --no-run-if-empty rm
	fi
}

HBM_BIN="/opt/fungible/bin/hbm_dump_pcie"
START_ADDR="0x0"
DUMP_MEM_SIZE="0x200000000" # 8GB
DPU_BUS_STR1="/sys/bus/pci/devices/0000:BUS:00.2/resource2"
HBM_COLLECT_NOTIFY="/tmp/HBM_Dump_Collection_In_Progress"

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

	# Touch a file so that user knows HBM dump collection
	# is in progress
	/usr/bin/touch $HBM_COLLECT_NOTIFY

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
	/bin/tar -cjf `echo $FILE_NAME.bz2` $FILE_NAME --remove-files
}

# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c()
{
        USER_CTRL_C=1
}


# Start of script

SSHPASS=`which sshpass`
if [[ -z $SSHPASS ]]; then
	apt-get install -y sshpass
fi

IPMITOOL=`which ipmitool`
if [[ -z $IPMITOOL ]]; then
	apt-get install -y ipmitool
fi

DPU_STATUS="/tmp/F1_STATUS"
DEST_DIR="/tmp/."
if [[ -d /sys/class/net/enp3s0f0.2 ]]; then
        BMC_IP="192.168.127.2"
else
	IPMI_LAN="ipmitool -U admin -P admin lan print 1"
	AWK_LAN='/IP Address[ ]+:/ {print $4}'
	BMC_IP=$($IPMI_LAN | awk "$AWK_LAN")
fi

printf "Poll BMC:  %s\n" $BMC_IP

BMC="-P password: -p superuser scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no sysadmin@$BMC_IP:$DPU_STATUS"

# Eg: Status from output from BMC
#--------------------+--------------------+
#  On Failure        | On Success         |
#--------------------+--------------------|
# cat /tmp/F1_STATUS | cat /tmp/F1_STATUS |
# STATUS: 0x00030000 | STATUS: 0x00000000 |
# F1_0: RUNNING      | F1_0: RUNNING      |
# F1_1: FAILED       | F1_1: RUNNING      |
#--------------------+--------------------+

# Detect the DPU PCIe Bus number
DetectDpuPcieBus

while true; do

	if [[ $USER_CTRL_C -eq 1 ]]; then
		break
	fi

	# Get the DPU status file from BMC
	# TODO: Cleaner mechanism to get status from BMC
	#       Currently using scp to get status from BMC
	DPU_HEALTH=$(sshpass $BMC $DEST_DIR > /dev/null 2>&1)

	# scan the results
	DPU0_HEALTH=`cat $DPU_STATUS | grep "F1_0" | cut -d " " -f 2`
	DPU1_HEALTH=`cat $DPU_STATUS | grep "F1_1" | cut -d " " -f 2`

	# We might have to disable this is future
	# This call is added to help flush the 
	# file-system cache to the disk
	# The over-ride is added so that we can
	# disable this check on a running system
	# if the performance deteriorates
	if [[ ! -f /tmp/disableContinuousFsSync ]]; then
		sync
	fi

	if [[ -z "$DPU0_HEALTH" ]] ||
	   [[ -z "$DPU1_HEALTH" ]]; then
		sleep $LOOP_INTERVAL
		continue
	fi

	if [[ "$DPU0_HEALTH" == "FAILED" ]] || [[ "$DPU1_HEALTH" == "FAILED" ]]; then
		if [[ "$DPU0_HEALTH" == "FAILED" ]] &&	\
		   [[ "$DPU0_HBM_DUMP_COLLECTED" == "0" ]]; then
			echo "Collecting HBM dump on DPU 0"
			CleanUpPrevDumps 0
			CollectHbmDump 0 $DPU_0_PCIE_BUS
			DPU0_HBM_DUMP_COLLECTED=1
			# Loop once more to check if the
			# other DPU is in FAILED state
			sleep $LOOP_INTERVAL
			continue
		fi

		if [[ "$DPU1_HEALTH" == "FAILED" ]] &&	\
		   [[ "$DPU1_HBM_DUMP_COLLECTED" == "0" ]]; then
			echo "Collecting HBM dump on DPU 1"
			CleanUpPrevDumps 1
			CollectHbmDump 1 $DPU_1_PCIE_BUS
			DPU1_HBM_DUMP_COLLECTED=1
			# Loop once more to check if the
			# other DPU is in FAILED state
			sleep $LOOP_INTERVAL
			continue
		fi

		if [[ -f $CONTINUOUS_REBOOT_COUNTER ]]; then
			VAL=`cat $CONTINUOUS_REBOOT_COUNTER`
			if [[ $VAL -ge $MAX_CONTINUOUS_REBOOTS ]]; then
				if [[ $STOP_REBOOTS -ne 1 ]]; then
					echo "$MAX_CONTINUOUS_REBOOTS continuous reboots reached"
					STOP_REBOOTS=1
				fi
			else
				VAL=$(( $VAL + 1 ))
				echo "$VAL" > $CONTINUOUS_REBOOT_COUNTER
			fi
		else
			echo "1" > $CONTINUOUS_REBOOT_COUNTER
		fi

		# Trigger FS1600 reset
		if [[ -f $FS1600_RESET ]] && [[ $STOP_REBOOTS -eq 0 ]]; then
			sync
			$FS1600_RESET
		fi
	fi

	UPTIME=`cat /proc/uptime | cut -d " " -f 1 | cut -d "." -f 1`
	if [[ $UPTIME -gt $NO_CONTINUOUS_REBOOT_TIME_MARK ]] && [[ $STOP_REBOOTS -eq 0 ]]; then
		if [[ -f $CONTINUOUS_REBOOT_COUNTER ]]; then
			echo "Deleting file $CONTINUOUS_REBOOT_COUNTER: count=`cat $CONTINUOUS_REBOOT_COUNTER`"
			rm -f $CONTINUOUS_REBOOT_COUNTER
		fi
	fi

	# Below 2 checks will work when DPU hot-plug is supported
	if [[ "$DPU0_HEALTH" == "RUNNING" ]] && [[ "$DPU0_HBM_DUMP_COLLECTED" == "1" ]]; then
		DPU0_HBM_DUMP_COLLECTED=0
	fi

	if [[ "$DPU1_HEALTH" == "RUNNING" ]] && [[ "$DPU1_HBM_DUMP_COLLECTED" == "1" ]]; then
		DPU1_HBM_DUMP_COLLECTED=0
	fi

	rm -f $DPU_STATUS

	sleep $LOOP_INTERVAL
done

