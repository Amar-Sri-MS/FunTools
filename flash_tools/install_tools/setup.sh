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
		echo "Upgrade error:" $trap_code > $LAST_ERROR
		echo -n "Last progress indicator: " >> $LAST_ERROR
		cat $PROGRESS >> $LAST_ERROR
		echo "Last stderr output:" >> $LAST_ERROR
		[ -s stderr.txt ] && cat stderr.txt >> $LAST_ERROR
	else
		log_msg "Install/Upgrade successful."
	fi
	rm -f $PROGRESS
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
ccfg_only=''
host_dpu=''
host_sku=''

if [ -e /sys/firmware/devicetree/base/fungible,dpu ] ; then
    read -d $'\0' host_dpu rest_of_line < /sys/firmware/devicetree/base/fungible,dpu
else
    host_dpu=$(dpcsh -Q peek config/processor_info/Model | jq -Mr .result)
fi

if [ -e /sys/firmware/devicetree/base/fungible,sku ] ; then
    read -d $'\0' host_sku rest_of_line < /sys/firmware/devicetree/base/fungible,sku
else
    host_sku=$(dpcsh -Q peek config/version/sku | jq -Mr .result)
fi

if [ -n "$host_dpu" ] && [ "$host_dpu" != "$CHIP_NAME" ]; then
	echo "This upgrade bundle is incompatible with the host DPU"
	echo "Bundle target: $CHIP_NAME, host DPU: $host_dpu"
	exit 20
fi

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
		ccfg-only=*)
			ccfg_install="ccfg-${1/ccfg-only=/}.signed.bin"
			ccfg_only='true'
			;;
		*)
			echo "
	Usage: sudo ${PROG}
		${PROG} install [ccfg=config_name]
		${PROG} install-downgrade [ccfg=config_name]
		${PROG} ccfg-only=config_name

	Where,
		Option install is to flash the DPU and install CCLinux software
		Option install-downgrade should be used when installing an older bundle to attempt
			DPU's firmware downgrade. This is not guaranteed to always work.
		If ccfg is specified, a file called ccfg-<config_name>.signed.bin will be programmed as ccfg.
		Option ccfg-only is to update ccfg only without performing a full system update
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
	log_msg "You may recover by removing $PROGRESS."
	exit 1
fi

# install the trap handler _after_ the initial in-progress check
trap "setup_err" HUP INT QUIT TERM ABRT EXIT

[[ $(id -u) != 0 ]] && log_msg "You need to be root to run the installer" && exit 1

dpc_upgrade_support=$(dpcsh -nQ fw_upgrade version | jq -Mr .result)
if [ "$dpc_upgrade_support" = "null" ]; then
	log_msg "FunOS does not support DPC-based upgrade. Cannot continue."
	exit 1
fi


echo "started" > $PROGRESS

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
pwd=$PWD

funos_sdk_version=$(sed -ne 's/^funsdk=\(.*\)/\1/p' .version || echo latest)

log_msg "Upgrading DPU firmware to $funos_sdk_version"

FW_UPGRADE_ARGS="--offline"

# run once to dump current fw information
./run_fwupgrade.py ${FW_UPGRADE_ARGS} --dry-run

# silence version checks for future runs of the script, as that
# makes the output logs hard to read
FW_UPGRADE_ARGS="$FW_UPGRADE_ARGS --no-version-check"

EXIT_STATUS=0

upgrade_interface_version=`dpcsh -nQ fw_upgrade version | jq -Mr ".result + 0"`
log_msg "Upgrade interface version = $upgrade_interface_version"

sbp_split_firmware=`dpcsh -nQ fw_upgrade sbp_split_firmware | jq -Mr ".result"`
log_msg "SBP split firmware support = $sbp_split_firmware"

CCFG_IMAGE_ID='ccfg'

if [[ $ccfg_only == 'true' ]]; then
	echo "CCFG update only!"
elif [[ "$DEV_IMAGE" -eq 1 ]]; then
	echo "Dev image upgrade!"

	dpcsh -Q peek config/chip_info/images/mmc1 | jq -Mre "[.result|.[]|.version | .==$funos_sdk_version] | any" > /dev/null
	RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error
	if [ $EXIT_STATUS -ne 0 ]; then
		bundles_found=$(dpcsh -Q peek config/chip_info/images/mmc1 | jq -Mr " [.result|.[]|.version] | @csv")
		log_msg "No matching release bundle found installed in the flash"
		log_msg "This bundle requires release bundle $funos_sdk_version to be installed, but only $bundles_found were found."
		exit 1
	fi
	./run_fwupgrade.py ${FW_UPGRADE_ARGS} --upgrade-file mmcx=mmc1_image.bin
	CCFG_IMAGE_ID='ccfx'
else
	if [[ $downgrade == 'true' ]]; then
		if [ -n "$host_sku" ]; then
			./run_fwupgrade.py ${FW_UPGRADE_ARGS} -u eepr --check-image-only --select-by-image-type "$host_sku"
			RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error
			if [ $EXIT_STATUS -ne 0 ]; then
				log_msg "This sku \"$host_sku\" is not supported by this bundle"
				exit 1
			fi

			./run_fwupgrade.py ${FW_UPGRADE_ARGS} -u bcfg --check-image-only --select-by-image-type "board_cfg_${host_sku}_default"
			RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error
			if [ $EXIT_STATUS -ne 0 ]; then
				log_msg "Default board config for the sku \"$host_sku\" is not supported by this bundle"
				exit 1
			fi
		fi

		./run_fwupgrade.py ${FW_UPGRADE_ARGS} -U --version latest --force --downgrade
		RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error

		if [[ "$sbp_split_firmware" == "true" ]]; then
			set_inactive_partition=$(dpcsh -Q boot_partition set_inactive | jq -Mr .result)
			case $set_inactive_partition in
				false)
					# should never happen, switching to inactive partition failed
					# indicate upgrade error but continue with the whole process anyway
					EXIT_STATUS=1
					;;
				true)
					: # marked inactive partition as the new boot default
					;;
				*)
					: # unexpected status
					log_msg "Unexpected set inactive partition result: $set_inactive_partition"
					EXIT_STATUS=1
					;;
			esac
		else
			log_msg "Old DPU firmware, downgrading active images"
			./run_fwupgrade.py ${FW_UPGRADE_ARGS} -U --version latest --force --downgrade --active
			RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error
		fi

		# Saved partition is not yet used for emmc images, so use old-style method
		# of erasing part of active image

		# a small hack until proper downgrade is supported; as we're only going to update
		# the inactive partition of funvisor data, erase enough of active funos image to make
		# it unbootable from uboot's perspective to force booing into (current) inactive.
		dd if=/dev/zero of=emmc_wipe.bin bs=1024 count=1024
		RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error

		./run_fwupgrade.py ${FW_UPGRADE_ARGS} --upgrade-file mmc1=emmc_wipe.bin --active
		RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error

		if [ -n "$host_sku" ]; then
			log_msg "Downgrading eepr \"$host_sku\""
			./run_fwupgrade.py ${FW_UPGRADE_ARGS} -u eepr --version latest --force --downgrade --select-by-image-type "$host_sku"
			RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error

			./run_fwupgrade.py ${FW_UPGRADE_ARGS} -u eepr --version latest --force --downgrade --active --select-by_image-type "$host_sku"
			RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error

			log_msg "Downgrading bcfg \"$host_sku\""
			./run_fwupgrade.py ${FW_UPGRADE_ARGS} -u bcfg --version latest --force --downgrade --select-by-image-type "board_cfg_${host_sku}_default"
			if [ $RC -eq 3 ]; then
				log_msg "Compatibility error. Aborting downgrade!"
				exit $RC
			fi
		fi
	else
		./run_fwupgrade.py ${FW_UPGRADE_ARGS} -U --version $funos_sdk_version
		RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error

		if [ $EXIT_STATUS -eq 2 ]; then
			log_msg "Aborting ... downgrade argument required"
			# exit early here, as this error code means no upgrade
			# was performed by run_fwupgrade script
			exit $EXIT_STATUS
		fi

		# in case a boot partition was stored in flash, erase it to boot
		# by default from a new (higher version) release

		# workaround for broken FunOS/SBP until all fixes propagate throughout the tree ...
		# When invoking a 'clear' and 'sbpf' entry does not exist in SBP's partition pointers, then
		# SBP would return an error. Some version of FunOS do not handle this SBP error which
		# leads to FunOS crash.
		# On one hand SBP should not crash when trying to clear a boot partition if it's never
		# been set before, on the other FunOS should not crash when SBP returns an error.
		# But since broken code exists in current tree, need to work around that through the extra
		# 'set_inactive' operation that would ensure 'sbpf' entry is created first.
		if [[ $upgrade_interface_version -lt 3 ]]; then
			if [[ "$sbp_split_firmware" == "true" ]]; then
				dpcsh -Q boot_partition set_inactive
			fi
		fi

		if [[ "$sbp_split_firmware" == "true" ]]; then
			dpcsh -Q boot_partition clear
		fi

		# skip eeprom and bcfg update on sdk bundles, as eepr images are not present
		if [ -n "$host_sku" ] && [ "$SDK_BUNDLE" -eq 0 ]; then
			log_msg "Updating eepr \"$host_sku\""
			./run_fwupgrade.py ${FW_UPGRADE_ARGS} -u eepr --select-by-image-type "$host_sku"
			RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error

			log_msg "Updating bcfg \"$host_sku\""
			./run_fwupgrade.py ${FW_UPGRADE_ARGS} -u bcfg --select-by-image-type "board_cfg_${host_sku}_default --version $funos_sdk_version"
			if [ $RC -eq 3 ]; then
				log_msg "Compatibility error. Aborting Upgrade!"
				exit $RC
			fi
		fi
	fi
fi

if [[ $ccfg_install ]]; then
	./run_fwupgrade.py ${FW_UPGRADE_ARGS} --upgrade-file $CCFG_IMAGE_ID=$ccfg_install
	RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error

	./run_fwupgrade.py ${FW_UPGRADE_ARGS} --upgrade-file $CCFG_IMAGE_ID=$ccfg_install --active
	RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error
else
	feature_set_resp=`dpcsh -nQ peek "config/boot_defaults/feature_set" || true`
	if echo -n "$feature_set_resp" | jq -Mre .result; then
		feature_set=`echo -n "$feature_set_resp" | jq -Mr .result`
		if [ ! -z "$feature_set" ]; then
			log_msg "Updating $CCFG_IMAGE_ID \"$feature_set\""
			./run_fwupgrade.py ${FW_UPGRADE_ARGS} -u $CCFG_IMAGE_ID --select-by-image-type "$feature_set"
			RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error
		fi
	else
		log_msg "Missing feature set"
	fi
fi

if [[ $ccfg_only == 'true' ]]; then
	# when executing via platform agent, STATUS_DIR will be set
	# to a folder where the bundle can store data persistently
	# Add a special stamp file for the upgrade verification to indicate
	# that the upgrade verification does not need to be performed
	# in this upgrade job
	if [[ -n "$STATUS_DIR" ]]; then
		echo "ccfg-only upgrade" > "$STATUS_DIR"/.no_upgrade_verify
	fi
	exit $EXIT_STATUS
fi

update_uboot_boot_debug_flag() {
	dpc_uboot_env.py --dpc-socket /tmp/dpc.sock get
	local current=$(fw_printenv -n boot_debug_fw 2>/dev/null)
	if [ "$current" != "$1" ]; then
		echo "Updating boot_debug flag to $1"
		fw_setenv boot_debug_fw $1
		dpc_uboot_env.py --dpc-socket /tmp/dpc.sock set
	fi
}

if [ ! -e /sys/firmware/devicetree/base/fungible,dpu ] ; then
	# if the installer was run outside of cclinux (eg. COMe) then
	# simply exit now before attempting cclinux fs upgrade
	exit $EXIT_STATUS
fi

if [[ "$DEV_IMAGE" -eq 1 ]]; then
	if [[ -n "$STATUS_DIR" ]]; then
		echo "dev-only upgrade" > "$STATUS_DIR"/.no_upgrade_verify
	fi
	# update u-boot env to enable dev image booting
	update_uboot_boot_debug_flag 1
	exit $EXIT_STATUS
else
	update_uboot_boot_debug_flag 0
fi

echo "DPU done" >> $PROGRESS

if [[ "$WITH_FUNVISOR" -eq 0 ]]; then
	log_msg "Bundle without CCLinux"
	sync
	exit $EXIT_STATUS
fi

log_msg "Upgrading CCLinux"

# Install partition table
./run_fwupgrade.py ${FW_UPGRADE_ARGS} --upgrade-file fgpt=fgpt.signed
# Update partition information
partprobe

install_and_verify_image() {
	local ifile=$1
	local ofile=$2
	local extra_flags=$3
	local isize=$(stat --printf="%s" $ifile)

	# calculate checksum of the installed image
	local isum=$(sha256sum $ifile | head -c 64)

	for retry in `seq 1 5`; do
		# program the image
		dd status=none if=$ifile of=$ofile $extra_flags

		sync $ofile; echo 3 > /proc/sys/vm/drop_caches

		# calculate checksum of the programmed image
		local osum=$(dd status=none if=$ofile count=1 bs=$isize | sha256sum | head -c 64)

		if [ "$isum" != "$osum" ]; then
			echo "$ifile -> $ofile: Programmed image checksum verification failed ($retry)"
		else
			echo "$ifile -> $ofile: Image programmed and verified ($retry)"
			return 0
		fi
	done
	return 1
}

# Install OS image
install_and_verify_image fvos.signed /dev/vdb1
RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error

# Install rootfs image
install_and_verify_image ${ROOTFS_NAME} /dev/vdb2 bs=4096
RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error

# Install rootfs hashtable
install_and_verify_image ${ROOTFS_NAME}.fvht.bin /dev/vdb4
RC=$?; [ $EXIT_STATUS -eq 0 ] && [ $RC -ne 0 ] && EXIT_STATUS=$RC # only set EXIT_STATUS to error on first error

# when executing via platform agent, STATUS_DIR will be set
# to a folder where the bundle can store data persistently
# store files before performing b-persist sync so that they
# are accessible after reboot into new fw
if [[ -n "$STATUS_DIR" ]]; then
	cp -a image.json "$STATUS_DIR"/image.json
	cp -a ${ROOTFS_NAME}.version "$STATUS_DIR"/version.sdk
	cp -a run_fwupgrade.py "$STATUS_DIR"/
fi

log_msg "Update config partition"

# special case for systems with unformatted/seriously corrupt b-persist
if ! grep -q b-persist /proc/mounts; then
	log_msg "No b-persist mountpoint found. Trying to mount ..."
	if ! mount /b-persist; then
		log_msg "Default mount failed, try remount/fixup"
		/usr/bin/b-persist mount-rw
	fi
fi

# standard setup with a read-only mounted b-persist
if grep -q "b-persist.*ro," /proc/mounts; then
	log_msg "Remounting b-persist in rw mode"
	/usr/bin/b-persist mount-rw
fi

# new rootfs should contain a periodic sync script generated by
# b-persist sync, but duplicate similar logic here for systems
# with old firmware that don't do that

CONFIG_SYNC_SCRIPT=/tmp/b-persist-sync

generate_config_script() {
echo """#!/bin/sh

while [ true ]; do
    rsync -ac --ignore-missing-args --delete /persist/config/ /b-persist/config
    rsync -ac --ignore-missing-args --delete /persist/upgrades/ /b-persist/upgrades
    sync /b-persist/config
    sync /b-persist/upgrades
    sleep 60
done

""" > ${CONFIG_SYNC_SCRIPT}
	chmod a+x ${CONFIG_SYNC_SCRIPT}
}

stop_sync_daemon() {
	start-stop-daemon -o -p ${CONFIG_SYNC_SCRIPT}.pid -K
}

start_sync_daemon() {
	start-stop-daemon -b -m -p ${CONFIG_SYNC_SCRIPT}.pid -x ${CONFIG_SYNC_SCRIPT} -S
}

# should be writable by now
if grep -q "b-persist.*rw," /proc/mounts; then
	log_msg "Sync configs"
	/usr/bin/b-persist sync

	if [ ! -f ${CONFIG_SYNC_SCRIPT} ]; then
		generate_config_script
		start_sync_daemon
	fi
fi

echo "CCLinux done" >> $PROGRESS

sync
exit $EXIT_STATUS
