#!/bin/bash
#
# File: mctp_transport_init.sh
# Purpose:
# Start/Stop/Restart Agent for MCTP Transport Services
#
# Created by Karnik Jain (karnik.jain@fungible.com)
# Copyright © 2022 Fungible. All rights reserved.
#

ST_STP_D=/sbin/start-stop-daemon
MCTP_TRANSPORT_PATH=/usr/bin
MCTP_TRANSPORT_GLUE_LAYER=mctp_transport.py
MCTP_TRANSPORT_TEMPERATURE_AGENT=mctp_tmp_agent.sh
MT_GL_PID_FILE=/tmp/${MCTP_TRANSPORT_GLUE_LAYER}.pid
MT_TA_PID_FILE=/tmp/${MCTP_TRANSPORT_TEMPERATURE_AGENT}.pid
MT_TA_POLLING_INT=3

if [[ ! -x ${ST_STP_D} ]] ||
   [[ ! -x ${MCTP_TRANSPORT_PATH}/${MCTP_TRANSPORT_GLUE_LAYER} ]] ||
   [[ ! -x ${MCTP_TRANSPORT_PATH}/${MCTP_TRANSPORT_TEMPERATURE_AGENT} ]]; then
	echo "Either of ${ST_STP_D}, ${MCTP_TRANSPORT_GLUE_LAYER}, ${MCTP_TRANSPORT_TEMPERATURE_AGENT} file is not found"
	exit 1
fi

start_mctp_transport_gluelayer()
{
	echo "Starting mctp glue-layer ${MCTP_TRANSPORT_PATH}/${MCTP_TRANSPORT_GLUE_LAYER}"

	OPTS="--background --make-pidfile --pidfile ${MT_GL_PID_FILE} --startas ${MCTP_TRANSPORT_PATH}/${MCTP_TRANSPORT_GLUE_LAYER}"
	CMD="--start"

	${ST_STP_D} ${OPTS} ${CMD}
}

start_mctp_temp_agent()
{
	echo "Starting mctp temperature agent ${MCTP_TRANSPORT_PATH}/${MCTP_TRANSPORT_TEMPERATURE_AGENT}"

	OPTS="--background --make-pidfile --pidfile ${MT_TA_PID_FILE} --startas ${MCTP_TRANSPORT_PATH}/${MCTP_TRANSPORT_TEMPERATURE_AGENT} ${MT_TA_POLLING_INT}"
	CMD="--start"

	${ST_STP_D} ${OPTS} ${CMD}
}

stop_by_pid()
{
	OPTS="--pidfile $1 --retry TERM/10/KILL/5"
	CMD="--stop"

	${ST_STP_D} ${OPTS} ${CMD} || true
	rm $1 || true
}

stop_mctp_gluelayer()
{
	echo "Stopping mctp glue-layer"
	stop_by_pid ${MT_GL_PID_FILE}
}

stop_mctp_tmp_agent()
{
	echo "Stopping mctp temperature agent"
	stop_by_pid ${MT_TA_PID_FILE}
}

case "$1" in
start)
	start_mctp_temp_agent
	start_mctp_transport_gluelayer	
	echo "done."
	;;

stop)
	stop_mctp_tmp_agent
	stop_mctp_gluelayer
	echo "done."
	;;

restart)
	stop_mctp_tmp_agent
	stop_mctp_gluelayer
	echo "stop done."

	start_mctp_temp_agent
	start_mctp_transport_gluelayer	
	echo "start done."
	;;

*)
	echo "Usage: /etc/init.d/mctp_transport_init {start|stop|restart}"
	exit 1
	;;
esac

exit 0

