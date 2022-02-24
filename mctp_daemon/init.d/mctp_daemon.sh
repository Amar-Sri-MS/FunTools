#!/bin/sh
# MCTP daemon start/stop script

RES_COL=60
MOVE_TO_COL="echo -en \\033[${RES_COL}G"
SETCOLOR_NORM="echo -en \\033[0;39m"
SETCOLOR_SUCC="echo -en \\033[1;32m"
SETCOLOR_FAIL="echo -en \\033[1;31m"

SERVICE=/usr/bin/mctp_daemon
LOCK_FILE=/tmp/mctp_daemon.lock

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


[ ! -x $SERVICE ] && die "mctp_daemon not found or not executable"

failed="no"

case "$1" in
start)
	echo -en "Starting ${SERVICE##*/} : "
	if [ -f $LOCK_FILE ]; then
	       	echo -en "Another service is running"
		fail
		exit 1
	fi
	$SERVICE -n -b >&/dev/null && pass || fail
	;;

stop)
	echo -en "Stoping ${SERVICE##*/} : "
	if [ ! -f $LOCK_FILE ]; then
	       echo -en "mctp_daemon isn't running"
	       fail
	       exit 1
       fi

	for pid in `cat $LOCK_FILE`; do
		if ps $pid >&/dev/null; then
			kill $pid || failed="yes"
			sleep 1
		fi
	done
	\rm -f $LOCK_FILE
	[ "$failed" == "yes" ] && fail || pass
	;;

*)
	die "Usage: ${0##*/} {start|stop}"
	;;
esac

exit 0

