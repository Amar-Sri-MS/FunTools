#!/bin/bash

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
	else
		log_msg "Install/Upgrade successful."
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

host_dpu=''
product=''

if [ -e /proc/device-tree/fungible,dpu ] ; then
    read -d $'\0' host_dpu rest_of_line < /proc/device-tree/fungible,dpu
else
    host_dpu=$(dpcsh -Q peek config/processor_info/Model | jq -Mr .result)
fi

if [ -e /proc/device-tree/fungible,product ]; then
    read -d $'\0' product rest_of_line < /proc/device-tree/fungible,product
else
    product=$(dpcsh -Q peek config/boot_defaults/PlatformInfo/product | jq -Mr .result)
fi

if [ -n "$host_dpu" ] && [ "$host_dpu" != "$CHIP_NAME" ]; then
	echo "This bundle is incompatible with the host DPU"
	echo "Bundle target: $CHIP_NAME, host DPU: $host_dpu"
	exit 20
fi
if [ "$product" != "$HW_BASE" ]; then
	echo "This bundle is incompatible with this hw platform"
	echo "Bundle target: $HW_BASE, hw platform: $product"
	echo "(if no hw platform is shown, the firmware must first be upgraded to a newer bundle)"
	exit 20
fi


# install the trap handler _after_ the initial in-progress check
trap "setup_err" HUP INT QUIT TERM ABRT EXIT

[[ $(id -u) != 0 ]] && log_msg "You need to be root to run the installer" && exit 1


boot_status=$(dpcsh -nQ peek "config/chip_info/boot_complete" | jq -Mr .result)
case $boot_status in
	null)
		: # boot status reporting not supported, assume complete
		;;
	true)
		: # boot complete, continue
		;;
	false)
		# booting still in progress
		log_msg "DPU has not finished booting, cannot start upgrade"
		exit 3
		;;
	*)
		: # unexpected status, assume complete for future compatibility
		log_msg "Unexpected boot complete status: $boot_status"
		;;
esac

log_msg "Installing and configuring cclinux software and DPU firmware"

FW_UPGRADE_ARGS="--offline --ws `pwd`"

# silence version checks for future runs of the script, as that
# makes the output logs hard to read
FW_UPGRADE_ARGS="$FW_UPGRADE_ARGS --no-version-check"

EXIT_STATUS=0


log_msg "Installing eepr \"$EEPR_NAME\""
./run_fwupgrade.py ${FW_UPGRADE_ARGS} -u eepr --version latest --force --downgrade --select-by-image-type "$EEPR_NAME"
RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error

./run_fwupgrade.py ${FW_UPGRADE_ARGS} -u eepr --version latest --force --downgrade --active --select-by-image-type "$EEPR_NAME"
RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error


# when executing via platform agent, STATUS_DIR will be set
# to a folder where the bundle can store data persistently
# store files before performing b-persist sync so that they
# are accessible after reboot into new fw
if [[ -n "$STATUS_DIR" ]]; then
	echo "eepr-only upgrade" > "$STATUS_DIR"/.no_upgrade_verify
fi

sync
exit $EXIT_STATUS
