#!/bin/bash -e

# .setup is generated as part of bundle generation to contain
# bundle-specific config variables
# note: busybox bash doesn't like 'source .setup'
source ./.setup

setup_err() {
	trap_code=$?
	set +x
	if [[ $trap_code -ne 0 ]]; then
		log_msg "Failed in setup. Please contact Fungible, Inc. support"
		[ -s stderr.txt ] && log_msg "STDERR is as follows:" && cat stderr.txt
		echo "Upgrade error:" $trap_code > $LAST_ERROR
		echo -n "Last progress indicator: " >> $LAST_ERROR
		cat $PROGRESS >> $LAST_ERROR
		echo "Last stderr output:" >> $LAST_ERROR
		[ -s stderr.txt ] && cat stderr.txt >> $LAST_ERROR
		rm -f $PROGRESS
	else
		log_msg "Install/Upgrade successful."
		echo "done" >> $PROGRESS
	fi
	sync
	exit $trap_code
}

log_msg() {
	echo "
[$(date '+%D %T')] $PROG: $1";
}


# main
PROG=$0
PROGRESS=/tmp/cclinux_upgrade_progress # a reboot will clean up this tmpfs file.
LAST_ERROR=/tmp/cclinux_upgrade_error # a reboot will clean up this tmpfs file.

ccfg_install=''
downgrade=''

if [[ $# -ne 0 ]]
then
	while [[ $# -gt 0 ]]
	do
		case $1 in
		install)
			;;
		install-downgrade)
			downgrade='true'
			;;
		ccfg=*)
			ccfg_install="ccfg-${1/ccfg=/}.signed.bin"
			;;
		*)
			echo "
	Usage: sudo ./${PROG}.sh
		${PROG}.sh install [ccfg=config_name]
		${PROG}.sh install-downgrade

	Where,
		Option install is to flash the DPU and install CCLinux software
		Option install-downgrade should be used when installing an older bundle to attempt
			DPU's firmware downgrade. This is not guaranteed to always work.
		If ccfg is specified, a file called ccfg-<config_name>.signed.bin will be programmed as ccfg.
	"
			exit 1;
			;;
		esac
		shift
	done
fi

if [ -f $PROGRESS ]
then
	log_msg "Previous upgrade in progress... Aborting..."
	log_msg "System should be rebooted to complete."
	log_msg "You may recover by removing $PROGRESS."
	exit 1
fi

# install the trap handler _after_ the initial in-progress check
trap "setup_err" HUP INT QUIT TERM ABRT EXIT

[[ $(id -u) != 0 ]] && log_msg "You need to be root to run the installer" && exit 1

echo "started" > $PROGRESS

log_msg "Installing and configuring cclinux software and DPU firmware"
pwd=$PWD

funos_sdk_version=$(sed -ne 's/^funsdk=\(.*\)/\1/p' .version || echo latest)

log_msg "Upgrading DPU firmware"

FW_UPGRADE_ARGS="--offline --ws `pwd`"

if [[ $downgrade ]]; then
	# downgrades are disabled because cclinux downgrade isn't supported
	# and they must always be kept in sync ...
	log_msg "Downgrade currently not supported"
	exit 1
	#./run_fwupgrade.py ${FW_UPGRADE_ARGS} -U --version latest --force --downgrade
	#./run_fwupgrade.py ${FW_UPGRADE_ARGS} -U --version latest --force --downgrade --active
else
	./run_fwupgrade.py ${FW_UPGRADE_ARGS} -U --version $funos_sdk_version
fi

if [[ $ccfg_install ]]; then
	./run_fwupgrade.py ${FW_UPGRADE_ARGS} --upgrade-file ccfg=$ccfg_install
	./run_fwupgrade.py ${FW_UPGRADE_ARGS} --upgrade-file ccfg=$ccfg_install --active
fi

echo "DPU done" >> $PROGRESS

log_msg "Upgrading CCLinux"

# Install partition table
./run_fwupgrade.py ${FW_UPGRADE_ARGS} --upgrade-file fgpt=fgpt.signed
# Update partition information
partprobe
# Install OS image
dd if=fvos.signed of=/dev/vdb1
# Install rootfs image
dd if=${ROOTFS_NAME} of=/dev/vdb2 bs=4096
# Install rootfs hashtable
dd if=${ROOTFS_NAME}.fvht.bin of=/dev/vdb4

echo "CCLinux done" >> $PROGRESS

sync
exit 0