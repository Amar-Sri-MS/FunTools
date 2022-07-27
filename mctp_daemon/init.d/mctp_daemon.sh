#!/bin/bash
#
# File: mctp_daemon.sh
# Purpose:
# Start/Stop/Restart Agent for MCTP Daemon &
# MCTP Transport Services
#
# Copyright © 2022 Fungible. All rights reserved.
#

RES_COL=60
MOVE_TO_COL="echo -en \\033[${RES_COL}G"
SETCOLOR_NORM="echo -en \\033[0;39m"
SETCOLOR_SUCC="echo -en \\033[1;32m"
SETCOLOR_FAIL="echo -en \\033[1;31m"

SERVICE=/usr/bin/mctp_daemon
LOCK_FILE=/tmp/mctp_daemon.lock

ST_STP_D=/sbin/start-stop-daemon
MCTP_TRANSPORT_PATH=/usr/bin
MCTP_TRANSPORT_GLUE_LAYER=mctp_transport.py
MCTP_TRANSPORT_TEMPERATURE_AGENT=mctp_tmp_agent.sh
MT_GL_PID_FILE=/tmp/${MCTP_TRANSPORT_GLUE_LAYER}.pid
MT_TA_PID_FILE=/tmp/${MCTP_TRANSPORT_TEMPERATURE_AGENT}.pid
MT_TA_POLLING_INT=3

UUID_FILE=/persist/config/mctp.uuid

die() {
	[ ! -z "$1" ] && echo "$1"
	exit 1
}

pass() {
        $MOVE_TO_COL; echo -n "["; $SETCOLOR_SUCC; echo -n "  OK  "; $SETCOLOR_NORM; echo  "]"
}

fail() {
        $MOVE_TO_COL; echo -n "["; $SETCOLOR_FAIL; echo -n "FAILED"; $SETCOLOR_NORM; echo  "]"
}

if [[ ! -x ${SERVICE} ]] ||
   [[ ! -x ${ST_STP_D} ]] ||
   [[ ! -x ${MCTP_TRANSPORT_PATH}/${MCTP_TRANSPORT_GLUE_LAYER} ]] ||
   [[ ! -x ${MCTP_TRANSPORT_PATH}/${MCTP_TRANSPORT_TEMPERATURE_AGENT} ]]; then
        die "Either of ${SERVICE}, ${ST_STP_D}, ${MCTP_TRANSPORT_GLUE_LAYER}, ${MCTP_TRANSPORT_TEMPERATURE_AGENT} not found or not executable"
	exit 1
fi

if [ ! -f $UUID_FILE ]; then
	cat /dev/urandom | tr -dc '0-9a-f' | head -c 32 > $UUID_FILE
fi

UUID=$(cat $UUID_FILE)

failed="no"

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

start_mctp_daemon()
{
	echo -en "Starting ${SERVICE##*/} : "
	if [ -f $LOCK_FILE ]; then
	       	echo -en "Another service is running"
		fail
		exit 1
	fi
	$SERVICE -n -b -l /persist/logs/mctp_daemon.log -u "$UUID" >&/dev/null && pass || fail
}

stop_mctp_daemon()
{
	echo -en "Stoping ${SERVICE##*/} : "
	if [ ! -f $LOCK_FILE ]; then
	       echo -en "mctp_daemon isn't running"
               exit 0
        fi

	for pid in `cat $LOCK_FILE`; do
		if ps $pid >&/dev/null; then
			kill $pid || failed="yes"
			sleep 1
		fi
	done
	\rm -f $LOCK_FILE
	[ "$failed" == "yes" ] && fail || pass
}

case "$1" in
start)
	start_mctp_daemon
	start_mctp_temp_agent
	start_mctp_transport_gluelayer	
	echo "done."
	;;

stop)
	stop_mctp_daemon
	stop_mctp_tmp_agent
	stop_mctp_gluelayer
	echo "done."
	;;

restart)
	stop_mctp_daemon
	stop_mctp_tmp_agent
	stop_mctp_gluelayer
	echo "stop done."

	start_mctp_daemon
	start_mctp_temp_agent
	start_mctp_transport_gluelayer	
	echo "start done."
	;;

*)
	die "Usage: ${0##*/} {start|stop|restart}"
	;;
esac

exit 0

