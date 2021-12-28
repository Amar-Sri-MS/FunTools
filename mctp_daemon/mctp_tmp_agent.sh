#!/bin/bash
#
# File: mctp_tmp_agent.sh
# Purpose: 
# Periodically Update MAX_TS_TEMP_VAL in following format to /tmp/.platform/MAX_DPU_TS_VAL.
# This would be consumed by MCTP Daemon to serve HostServer's "GetSensorReading PLDM Command"
# 	Format:
#	<SensorID_1> <MAX_TS_TEMP_VAL_1>
#	<SensorID_2> <TEMP_VAL_2>
#	... so on ...
# Also whenever MAX_TEMP_VAL crosses warning, critical or fatal temperature threshold values,
# it would also periodically writes to MCTP Daemon's /tmp/mctp_sensors (in same above format)
# till that condition goes off.
# Once such conditions totally goes off then it would write only once last time to this FIFO to
# indicate MCTP to clear the temp_condition and then never write to that FIFO again till such
# condition arises in future.
#
# Created by Karnik Jain (karnik.jain@fungible.com)
# Copyright © 2021 Fungible. All rights reserved.
#
#

MINARGS=1
MAXARGS=1

Usage() {
	echo "${0} <Thermal Polling Interval in Seconds>"
}

if [ ${#} -lt ${MINARGS} -o ${#} -gt ${MAXARGS} ]; then
	Usage
	exit 1
fi

POLL_INTERVAL=${1}
MCTP_FIFO="/tmp/mctp_sensors"
MAX_TEMP=127
MIN_TEMP=-127
DPCSH_CMD="/usr/bin/dpcsh -c/tmp/dpc.sock --nocli-quiet"

DPU_HIGH_THRESHOLD=95

PLATFORM_LOG_DIR="/tmp/.platform"
/bin/mkdir -p ${PLATFORM_LOG_DIR}
MCTP_TEMP_LOG="$PLATFORM_LOG_DIR/MAX_DPU_TS_VAL"

SendEventToMCTP() {
	if [ -z "${1}" -o -z "${2}" -o -z "${3}" ]; then
		return 1
	fi

	local TS_TEMP_INDEX=${1}
	local MAX_TS_TEMP=${2}
	local TS_WARN_TEMP=${3}
	local TS_TEMP_WAR_ASSERT=0

	#Write to MCTP Named FIFO, if it exists
	if [ -p ${MCTP_FIFO} ]; then
		if [ ${MAX_TS_TEMP} -gt ${TS_WARN_TEMP} ]; then
			/bin/echo "${TS_TEMP_INDEX} ${MAX_TS_TEMP}" > ${MCTP_FIFO}
			TS_TEMP_WAR_ASSERT=1
			echo "Insyde ..."
		elif [ ${MAX_TS_TEMP} -lt ${TS_WARN_TEMP} -a ${TS_TEMP_WAR_ASSERT} -eq 1 ]; then
			/bin/echo "${TS_TEMP_INDEX} ${MAX_TS_TEMP}" > ${MCTP_FIFO}
			TS_TEMP_WAR_ASSERT=0
		fi
	fi

	#Log to a File as well
	if [ ${TS_TEMP_INDEX} -eq 1 ]; then
		/bin/echo "${TS_TEMP_INDEX} ${MAX_TS_TEMP}" > ${MCTP_TEMP_LOG}
	else 
		/bin/echo "${TS_TEMP_INDEX} ${MAX_TS_TEMP}" >> ${MCTP_TEMP_LOG}
	fi
}

GetDPUSensorsThermal() {
	if [ -z "${1}" ]; then
		return 1
	fi

	local TS_ID=${1}
	local MAX_DPU_TEMP=-127
	local DPU_SNR_CNT=9
	local CNT=0
	#DPU TS Thresolds as per System team
	local DPU_WARN_TEMP=$((DPU_HIGH_THRESHOLD - 25))
	local DPU_CRIT_TEMP=$((DPU_HIGH_THRESHOLD - 10))
	local DPU_FATAL_TEMP=$((DPU_HIGH_THRESHOLD - 3))

	while [ ${CNT} -lt ${DPU_SNR_CNT} ]; do
		DPU_TS_GET_CMD=$(${DPCSH_CMD} temperature dpu ${CNT})
		if [ ${?} -ne 0 ]; then
			continue
		fi

		DPU_TEMP=$(/bin/echo ${DPU_TS_GET_CMD} | /usr/bin/jq -r .result.temperature)
		if [ ! -z "${DPU_TEMP}" ]; then
			#Ignore All Read Temp which are <-127*C or > 127*C
			if [ ${DPU_TEMP} -lt ${MAX_TEMP} -a ${DPU_TEMP} -gt ${MIN_TEMP} ]; then
				if [ ${DPU_TEMP} -gt ${MAX_DPU_TEMP} ]; then
					MAX_DPU_TEMP=${DPU_TEMP}
				fi
			fi
		fi
		CNT=$((CNT + 1))
	done
	SendEventToMCTP ${TS_ID} ${MAX_DPU_TEMP} ${DPU_WARN_TEMP}
}

#Poll every $POLL_INTERVAL
while true; do
	SENSOR_ID=1
	GetDPUSensorsThermal ${SENSOR_ID}
	sleep $POLL_INTERVAL
done
