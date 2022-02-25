#!/bin/bash

die() {
	[ ! -z "$1" ] && echo "$1"
	exit 1
}

# this envs should come from projectdb.json
[ -z $MCTP_DAEMON_INSTALL_DIR ] && die $"Error - missing install dir"
[ -z $DEPLOY_ROOT ] && die $"Error - missing deploy root"

: ${STARTUP_ID=-90}
rc_script=mctp_daemon.sh

mkdir -p $DEPLOY_ROOT/usr/bin
cp -f $MCTP_DAEMON_INSTALL_DIR/etc/init.d/$rc_script $DEPLOY_ROOT/etc/init.d
cp -f $MCTP_DAEMON_INSTALL_DIR/usr/bin/{mctp_daemon,mctp_tmp_agent.sh,mctp_transport.py} $DEPLOY_ROOT/usr/bin

mkdir -p $DEPLOY_ROOT/etc/rc5.d
cd ${DEPLOY_ROOT}/etc/rc5.d
ln -sf ../init.d/$rc_script S${STARTUP_ID}mctp_daemon
