#! /bin/sh
set -e

PID_DPC=/var/run/dpc-funtail.pid
PID_FUNTAIL=/var/run/funtail.pid

# source function library
. /etc/init.d/functions

# /etc/init.d/funtail: start and stop the Fungible "funtail" logger

export PATH="${PATH:+$PATH:}/usr/sbin:/sbin:/usr/bin"

case "$1" in
  start)
	echo "Starting FunOS log streamer: funtail"
	start-stop-daemon -S -b -p $PID_DPC -x /usr/bin/dpcsh -- --unix_proxy
	start-stop-daemon -S -b -p $PID_FUNTAIL -- -u /tmp/funos-dpc-text.sock -f -s0
	echo "done."
	;;
  stop)
	echo "Stopping FunOS log streamer: funtail"
	start-stop-daemon -K -p $PID_DPC -x /usr/bin/dpcsh
	start-stop-daemon -K -p $PID_FUNTAIL
	echo "."
	;;
  *)
	echo "Usage: /etc/init.d/funtail {start|stop}"
	exit 1
esac

exit 0
