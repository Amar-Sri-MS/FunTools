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

if [[ "$EUID" -ne 0 ]]; then
        printf "Please run as ROOT EUID=$EUID\n"
        exit
fi

#SWSYS-604
INTERNAL_VLAN_VIRT_INTF="/sys/class/net/enp3s0f0.2"
if [[ -d $INTERNAL_VLAN_VIRT_INTF ]]; then
        UP_STATE=`cat $INTERNAL_VLAN_VIRT_INTF/operstate`
        if [[ $UP_STATE == "down" ]]; then
                echo "Interface $INTERNAL_VLAN_VIRT_INTF is in down state"
                netplan apply
        fi
fi

LOOP_INTERVAL=5
DPU0_HBM_DUMP_COLLECTED=0
DPU1_HBM_DUMP_COLLECTED=0
USER_CTRL_C=0
FS1600_RESET="/opt/fungible/etc/ResetFs1600.sh"
DUMP_ASSEMBLY="/opt/fungible/etc/DpuAssembleDump.py"
NO_CONTINUOUS_REBOOT_TIME_MARK=1200
CONTINUOUS_REBOOT_COUNTER="/var/log/fs1600_reboot_counter"
STOP_REBOOTS=0
MAX_CONTINUOUS_REBOOTS=3

FILE_BLD_NUM="/opt/fungible/.version"

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


HBM_COLLECT_NOTIFY="/tmp/HBM_Dump_Collection_In_Progress"
function CollectHbmDump()
{
	if [[ $# -ne 1 ]]; then
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

	set +e
	echo "$DUMP_ASSEMBLY $BMC_MAC $DPU $BLD_NUM"
	$DUMP_ASSEMBLY $BMC_MAC $DPU $BLD_NUM

	if [ $? -eq 2 ]; then
		sync
		echo "Single DPU collection timed out"
	fi

	set -e
}

# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c()
{
        USER_CTRL_C=1
}


# Start of script

MINARGS=0
MAXARGS=1

MONOSHOT_MODE=0
if [[ ${#} -eq ${MAXARGS} ]]; then
	FAILED_DPU_MASK=${1}
	MONOSHOT_MODE=1
fi

# Don't allow second instance
ME="${0}"
PROG=$(/usr/bin/basename "${ME}")

PROG_RUNNING_INDICATOR="/tmp/.${PROG}.running"

if [[ -f ${PROG_RUNNING_INDICATOR} ]]; then
	echo "${0}: Cannot start second instance"
	exit 1
fi

touch ${PROG_RUNNING_INDICATOR}

DPU_STATUS="/tmp/F1_STATUS"
DEST_DIR="/tmp/."

if [[ -d /sys/class/net/enp3s0f0.2 ]]; then
        BMC_IP="192.168.127.2"
else
	IPMI_LAN="ipmitool lan print 1"
	AWK_LAN='/IP Address[ ]+:/ {print $4}'
	BMC_IP=$($IPMI_LAN | awk "$AWK_LAN")
fi
BMC_MAC=`ipmitool lan print 1 | awk '/MAC Address[ ]+:/ {print $4}'`
echo "BMC_IP=${BMC_IP} BMC_MAC=${BMC_MAC}"

if [[ ${MONOSHOT_MODE} -eq 0 ]]; then
	printf "Poll BMC:  %s\n" $BMC_IP
fi

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

# This file is set once BMC-COMe heartbeat monitoring is
# established. This feature is not availabe on Rev1/Rev1+
# system (legacy) and hence on those systems we resort to
# legacy HBM dump processing wherein this script loops
SUSPEND_DPU_HEALTH_MONITORING_FLAG="/tmp/.SuspendDpuHealthMonitoring"

# Detect the DPU PCIe Bus number
DetectDpuPcieBus

while true; do

	if [[ $USER_CTRL_C -eq 1 ]]; then
		break
	fi

	# If BMC has asked to suspend DPU health monitoring
	# then exit from this script with a message
	# The next time this sctipt gets called (from BMC)
	# It will perform the same way it will work in normal
	# polling mode however it's a monoshot operation
	if [[ -f ${SUSPEND_DPU_HEALTH_MONITORING_FLAG} ]]; then
		if [[ ${MONOSHOT_MODE} -eq 0 ]]; then
			echo "Exit ${0} because switching to monoshot mode for HBM processing"
			echo "BMC will trigger this script upon F1 failure"
			rm -f ${PROG_RUNNING_INDICATOR}
			rm -f ${CONTINUOUS_REBOOT_COUNTER}
			exit 0
		fi

		if [[ -z "${FAILED_DPU_MASK}" ]]; then
			echo "Expects which DPU# to process HBM"
			exit 1
		fi

		if [[ ${FAILED_DPU_MASK} -eq 1 ]]; then
			DPU0_HEALTH="FAILED"
		elif [[ ${FAILED_DPU_MASK} -eq 2 ]]; then
			DPU1_HEALTH="FAILED"
		elif [[ ${FAILED_DPU_MASK} -eq 3 ]]; then
			DPU0_HEALTH="FAILED"
			DPU1_HEALTH="FAILED"
		else
			echo "Incorrect DPU mask ${FAILED_DPU_MASK}"
			exit 1
		fi

		sync
	else
		# Below code is for legacy support
		# This code will still be used by Rev1/Rev1+ systems
		# running older BMC firmware

		# Get the DPU status file from BMC
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

		# SWSYS-950: Print a banner to notify user that
		# unsupported config of chassis+system bundle is
		# installed on the system. (Fine for Rev1/Rev1+)
		Unsupported_Config_Banner
	fi

	if [[ "$DPU0_HEALTH" == "FAILED" ]] || [[ "$DPU1_HEALTH" == "FAILED" ]]; then
		if [[ "$DPU0_HEALTH" == "FAILED" ]] &&	\
		   [[ "$DPU0_HBM_DUMP_COLLECTED" == "0" ]]; then
			echo "Collecting HBM dump on DPU 0"
			CollectHbmDump 0
			DPU0_HBM_DUMP_COLLECTED=1
			# Loop once more to check if the
			# other DPU is in FAILED state
			sleep $LOOP_INTERVAL
			continue
		fi

		if [[ "$DPU1_HEALTH" == "FAILED" ]] &&	\
		   [[ "$DPU1_HBM_DUMP_COLLECTED" == "0" ]]; then
			echo "Collecting HBM dump on DPU 1"
			CollectHbmDump 1
			DPU1_HBM_DUMP_COLLECTED=1
			# Loop once more to check if the
			# other DPU is in FAILED state
			sleep $LOOP_INTERVAL
			continue
		fi

		# When this script is running in a monoshot mode
		# it is indirectly being driven from BMC
		# The system reboot request after completion of
		# HBM processing is left to the BMC and hence we
		# return from this script at this point
		if [[ ${MONOSHOT_MODE} -eq 1 ]]; then
			sync
			exit 0
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

