#!/bin/bash -e
# Generate a NOR flash image for use by SBP inside the SBP build container.
#
# Assumes that it starts execution in the root directory of the container.
# The /build directory is the Jenkins workspace for the build, with SBP
# checked out in that directory.
#

ARTIFACT_STYLE=
BOOT_SIG_TYPE=
CUSTOM_HOST_FIRMWARE=
CUSTOMER_CONFIG_JSON=
CUSTOMER_OTP_ARGS=
VARIANT=
CHIP=
OTP_CHIP=
OTP_SERIAL_NR=
OTP_MODE=
OTP_CHALLENGE=
EMULATION=0
WORKSPACE=${WORKSPACE:-/build}

print_usage_and_exit()
{
	echo "Usage: genimage.sh -v <variant> -s {unsecure|no,fungible|yes,customer} -f <firmware_for_host> -e <0/1> -c <f1|s1|f1d1|s2> [-C {i2c,jtag}]"
	echo -n " <firmware_for_host> is path to the host software to be embedded in flash"
	echo -e "\nExample: build.sh -v fungible_eeprom_zynq6 -s fungible -f u_boot.bin -e\n"
	exit $1
}

check_for_fpk1_modulus()
{
	if [ ! -f $SBP_ROOT_DIR/software/production/$1 ]; then
		echo "could not find the modulus file \"$1\" in $SBP_ROOT_DIR/software/production"
		exit 1
	fi
}

validate_process_input()
{
	if [ -z $VARIANT ]; then
		echo " -v variant option is missing"
		print_usage_and_exit 1
	fi

	case "$CHIP" in
		f1|s1|f1d1)
		OTP_SERIAL_NR=0x1234
		check_for_fpk1_modulus fpk1_modulus.c
		;;
		s2|f2)
		OTP_SERIAL_NR=0x1236
		check_for_fpk1_modulus fpk1s2_modulus.c
		;;
		*)
			echo " -c chip option is missing or incorrect: $CHIP"
			print_usage_and_exit 1
		esac

	OTP_CHIP=`echo "$CHIP" | tr '[:lower:]' '[:upper:]'`

	case "$BOOT_SIG_TYPE" in
		customer)
			CUSTOMER_CONFIG_JSON=$WORKSPACE/FunSDK/bin/flash_tools/qspi_config_customer.json
			ARTIFACT_STYLE=customer_$VARIANT
			OTP_MODE=secure
			;;
		fungible|yes)
			BOOT_SIG_TYPE=fungible # clamp to fungible
			ARTIFACT_STYLE=secure_$VARIANT
			OTP_MODE=secure
			;;
		unsecure|no)
			BOOT_SIG_TYPE=unsecure # clamp to unsecure
			ARTIFACT_STYLE=unsecure_$VARIANT
			OTP_MODE=unsecure
			;;
		*)
			echo " -s invalid value: [$BOOT_SIG_TYPE]"
			print_usage_and_exit 1
	esac

	if [ -z $CUSTOM_HOST_FIRMWARE ]; then
		echo " -f host firmware option is missing"
		print_usage_and_exit 1
	fi

	case "$OTP_CHALLENGE" in
		i2c|jtag)
			OTP_CHALLENGE="--challenge $OTP_CHALLENGE"
			;;
		"")
			# empty OTP_CHALLENGE is ok, nothing to do
			;;
		*)
			echo " Invalid otp challenge option, must be 'i2c' or 'jtag'"
			print_usage_and_exit 1
			;;
	esac
}

while getopts e:v:s:hf:c:C: arg;
do
	case $arg in
	v)	VARIANT="$OPTARG";;
	s)	BOOT_SIG_TYPE=`echo "$OPTARG" | tr '[:upper:]' '[:lower:]'`;;
	f)	CUSTOM_HOST_FIRMWARE="$OPTARG";;
	e)	EMULATION=$OPTARG;;
	c)	CHIP=$OPTARG;;
	C)	OTP_CHALLENGE=$OPTARG;;
	h)	print_usage_and_exit 0;;
	*)	print_usage_and_exit 1;;
	esac
done

cd ${WORKSPACE}

# Copy SBP products into common location.
mkdir -p ${WORKSPACE}/sbpimage/archive

pushd SBPFirmware

SBP_ROOT_DIR=`pwd`
SBP_INSTALL_DIR=`cd build/install && pwd`
SBP_BUILD_DIR=`cd build/build_src && pwd`
SBP_DEVTOOLS_DIR=`cd software/devtools/firmware && pwd`
popd

validate_process_input

export WORKSPACE # scripts invoked from here expect it to be set


# ---- ROM ----
cp $SBP_INSTALL_DIR/bootloader_m5150.mif ${WORKSPACE}/sbpimage/SysROM
# || true is added because the .codefile might not be always there
cp $SBP_INSTALL_DIR/bootloader_m5150.codefile ${WORKSPACE}/sbpimage/SysROM.codefile || true


mkdir -p artifacts_$ARTIFACT_STYLE && cd artifacts_$ARTIFACT_STYLE

HOST_FIRMWARE_DEF=$(cat <<-JSON
{ "signed_images": {
     "host_firmware_packed.bin": {
         "source":"${CUSTOM_HOST_FIRMWARE}"
         }
     }
}
JSON
)

EEPROM_DEF=$(cat <<-JSON
{ "signed_images": {
     "eeprom_packed.bin": {
         "source":"${VARIANT}"
         }
     }
}
JSON
)

QSPI_EMULATION=$(cat <<-JSON
{
	"output_format": {
        "size": "0x200000",
        "page": "0x10000",
        "output": "qspi_image_emu"
    },
	"output_sections": {
		"HOST": {
			"B": "",
			"minsize": "0"
		},
		"FIRMWARE": {
			"minsize" : "0"
		},
		"PUF-ROM": {
			"minsize" : "0"
		}
	}
}
JSON
)

prefix="eeprom_"
board_name=${VARIANT#"$prefix"}

BOARD_CFG_DEF=$(cat <<-JSON
{ "signed_images": {
     "board_cfg.bin": {
         "source":"board_cfg_${board_name}_default"
         }
     }
}
JSON
)

case "$CHIP" in
	f1|s1|f1d1|s2)
	hbsb_file=sbus_master.hbm.conv.rom
	;;
	f2)
	hbsb_file="f2-hbm.emu.rom"
	;;
esac

HBM_SBUS_CFG_DEF=$(cat <<-JSON
{ "signed_images": {
     "hbm_sbus.bin": {
       "source": "${hbsb_file}",
       "description": "@file:${hbsb_file}.version"
        }
    }
}
JSON
)

if [ $EMULATION == 0 ]; then
	# generate flash image for real chip
	python3 $WORKSPACE/FunSDK/bin/flash_tools/generate_flash.py --config-type json \
		--source-dir $SBP_INSTALL_DIR \
		--source-dir $WORKSPACE/FunSDK/FunSDK/dpu_eepr \
		--source-dir $WORKSPACE/FunSDK/FunSDK/sbpfw/roms \
		--source-dir $WORKSPACE/FunSDK/feature_sets/boardcfg/${CHIP} \
		--fail-on-error \
		--chip $CHIP \
		$WORKSPACE/FunSDK/bin/flash_tools/qspi_config_fungible.json \
		$WORKSPACE/FunSDK/bin/flash_tools/key_bag_config.json \
		$CUSTOMER_CONFIG_JSON \
		<(echo $HOST_FIRMWARE_DEF) \
		<(echo $EEPROM_DEF) \
		<(echo $BOARD_CFG_DEF) \
		<(echo $HBM_SBUS_CFG_DEF)
	# Flash images for real hardware
	cp qspi_image_hw.byte ${WORKSPACE}/sbpimage/flash_image_hw.byte
	cp qspi_image_hw.bin ${WORKSPACE}/sbpimage/flash_image_hw.bin
	# FIXME: other scripts still expect flash_image files, so create copies here
	cp qspi_image_hw.byte ${WORKSPACE}/sbpimage/flash_image.byte
	cp qspi_image_hw.bin ${WORKSPACE}/sbpimage/flash_image.bin
else
	# get the well-known enrollment certificate for emulation
	wget "https://f1reg.fungible.com/cgi-bin/enrollment_server.cgi/?cmd=cert&sn=`printf \"%048x\" $OTP_SERIAL_NR`" -O - \
		| base64 -d - > ${WORKSPACE}/enroll_cert.bin
	# generate flash image for emulation
	python3 $WORKSPACE/FunSDK/bin/flash_tools/generate_flash.py --config-type json \
		--source-dir $SBP_INSTALL_DIR \
		--source-dir $WORKSPACE/FunSDK/FunSDK/dpu_eepr \
		--source-dir $WORKSPACE/FunSDK/FunSDK/sbpfw/roms \
		--source-dir $WORKSPACE/FunSDK/feature_sets/boardcfg/${CHIP}-emu \
		--enroll-cert ${WORKSPACE}/enroll_cert.bin \
		--fail-on-error \
		--chip $CHIP \
		$WORKSPACE/FunSDK/bin/flash_tools/qspi_config_fungible.json \
		$WORKSPACE/FunSDK/bin/flash_tools/key_bag_config.json \
		$CUSTOMER_CONFIG_JSON \
		<(echo $HOST_FIRMWARE_DEF) \
		<(echo $EEPROM_DEF) \
		<(echo $QSPI_EMULATION) \
		<(echo $BOARD_CFG_DEF) \
		<(echo $HBM_SBUS_CFG_DEF)
	# Flash images for Palladium emulation (limited to 2MB)
	cp qspi_image_emu.byte ${WORKSPACE}/sbpimage/flash_image.byte
	cp qspi_image_emu.bin ${WORKSPACE}/sbpimage/flash_image.bin

	# OTP -- only for emulation
	mkdir -p OTP
	PWD=`pwd`


	if [ $BOOT_SIG_TYPE == customer ]; then
		CUSTOMER_OTP_ARGS="--key_hash $PWD/key_hash1.bin --key_hash $PWD/key_hash2.bin"
		if [ $OTP_CHIP == "F2" ]; then
			CUSTOMER_OTP_ARGS="${CUSTOMER_OTP_ARGS} --key_hash $PWD/key_hash3.bin --key_hash $PWD/key_hash4.bin"
		fi
	 fi

	# Remove the MIF extension - these actually aren't in MIF format, and
	# Rajesh's scripts for running jobs in emulation will do the needed
	# conversions.

	$SBP_DEVTOOLS_DIR/generate_otp.py \
            --cm_input $SBP_DEVTOOLS_DIR/otp_templates/OTP_content_CM.txt \
            --sm_input $SBP_DEVTOOLS_DIR/otp_templates/OTP_content_SM.txt \
            --ci_input $SBP_DEVTOOLS_DIR/otp_templates/OTP_content_CI_${OTP_CHIP}.txt \
            --esecboot $OTP_MODE --serial_nr $OTP_SERIAL_NR $CUSTOMER_OTP_ARGS \
            $OTP_CHALLENGE \
            --output ${WORKSPACE}/sbpimage/OTP_memory
fi


cp -r ${WORKSPACE}/artifacts_$ARTIFACT_STYLE/ ${WORKSPACE}/sbpimage/archive

# copy bootloaders
cd $SBP_BUILD_DIR
find . -name "bootloader_m5150.*" -print | xargs tar cf - | (cd ${WORKSPACE}/sbpimage; tar xf -)

exit 0
