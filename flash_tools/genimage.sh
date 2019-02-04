#!/bin/bash -e
# Generate a NOR flash image for use by SBP inside the SBP build container.
#
# Assumes that it starts execution in the root directory of the container.
# The /build directory is the Jenkins workspace for the build, with SBP
# checked out in that directory.
#

ARTIFACT_STYLE=
SECURE_BOOT=
BOOT_SIG_TYPE=
CUSTOM_HOST_FIRMWARE=
CUSTOMER_CONFIG_JSON=
CUSTOMER_OTP_ARGS=
VARIANT=
EMULATION=0
WORKSPACE=${WORKSPACE:-/build}

print_usage_and_exit()
{
	echo "Usage: genimage.sh -v <variant> -s {unsecure|no,fungible|yes,customer} -f <firmware_for_host> -e <0/1>"
	echo -n " <firmware_for_host> is path to the host software to be embedded in flash"
	echo -e "\nExample: build.sh -v fungible_eeprom_zynq6 -s fungible -f u_boot.bin -e\n"
	exit $1
}

validate_process_input()
{
	if [ -z $VARIANT ]; then
		echo " -v variant option is missing"
		print_usage_and_exit -1
	fi
	case "$BOOT_SIG_TYPE" in
		customer)
			SECURE_BOOT=yes
			CUSTOMER_CONFIG_JSON=$WORKSPACE/FunSDK/bin/flash_tools/qspi_config_customer.json
			ARTIFACT_STYLE=customer_$VARIANT
			;;
		fungible|yes)
			BOOT_SIG_TYPE=fungible
			SECURE_BOOT=yes
			ARTIFACT_STYLE=secure_$VARIANT
			;;
		unsecure|no)
			BOOT_SIG_TYPE=unsecure
			SECURE_BOOT=no
			ARTIFACT_STYLE=unsecure_$VARIANT
			;;
		*)
			echo " -s invalid value: [$BOOT_SIG_TYPE]"
			print_usage_and_exit -1
	esac
	if [ -z $CUSTOM_HOST_FIRMWARE ]; then
		echo " -f host firmware option is missing"
		print_usage_and_exit -1
	fi
}

while getopts e:v:s:hf: arg;
do
	case $arg in
	v)	VARIANT="$OPTARG";;
	s)	BOOT_SIG_TYPE=`echo "$OPTARG" | tr '[:upper:]' '[:lower:]'`;;
	f)	CUSTOM_HOST_FIRMWARE="$OPTARG";;
	e)	EMULATION=$OPTARG;;
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

popd

validate_process_input

export WORKSPACE # scripts invoked from here expect it to be set

# ---- ROM ----
cp $SBP_INSTALL_DIR/bootloader_m5150.mif ${WORKSPACE}/sbpimage/SysROM

mkdir -p artifacts_$ARTIFACT_STYLE && cd artifacts_$ARTIFACT_STYLE

$WORKSPACE/FunSDK/bin/flash_tools/get_start_cert.sh

HOST_FIRMWARE_DEF=$(cat <<-JSON
{ "signed_images": {
     "host_firmware_packed_v1.bin": {
         "source":"${CUSTOM_HOST_FIRMWARE}"
         }
     }
}
JSON
)

EEPROM_DEF=$(cat <<-JSON
{ "signed_images": {
     "eeprom_packed_v1.bin": {
         "source":"${VARIANT:9}"
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
		}
	}
}
JSON
)

if [ $EMULATION == 0 ]; then
	# generate flash image for real chip
	python3 $WORKSPACE/FunSDK/bin/flash_tools/generate_flash.py --config-type json \
		--source-dir $SBP_INSTALL_DIR \
		--source-dir $SBP_ROOT_DIR/software/eeprom \
		$WORKSPACE/FunSDK/bin/flash_tools/qspi_config_fungible.json \
		$CUSTOMER_CONFIG_JSON \
		<(echo $HOST_FIRMWARE_DEF) \
		<(echo $EEPROM_DEF)
	# Flash images for real hardware
	cp qspi_image_hw.byte ${WORKSPACE}/sbpimage/flash_image_hw.byte
	cp qspi_image_hw.bin ${WORKSPACE}/sbpimage/flash_image_hw.bin
	# FIXME: other scripts still expect flash_image files, so create copies here
	cp qspi_image_hw.byte ${WORKSPACE}/sbpimage/flash_image.byte
	cp qspi_image_hw.bin ${WORKSPACE}/sbpimage/flash_image.bin
else
	# generate flash image for emulation
	python3 $WORKSPACE/FunSDK/bin/flash_tools/generate_flash.py --config-type json \
		--source-dir $SBP_INSTALL_DIR \
		--source-dir $SBP_ROOT_DIR/software/eeprom \
		--enroll-tbs ${WORKSPACE}/enroll_tbs.bin \
		$WORKSPACE/FunSDK/bin/flash_tools/qspi_config_fungible.json \
		$CUSTOMER_CONFIG_JSON \
		<(echo $HOST_FIRMWARE_DEF) \
		<(echo $EEPROM_DEF) \
		<(echo $QSPI_EMULATION)
	# Flash images for Palladium emulation (limited to 2MB)
	cp qspi_image_emu.byte ${WORKSPACE}/sbpimage/flash_image.byte
	cp qspi_image_emu.bin ${WORKSPACE}/sbpimage/flash_image.bin
fi

# ---- OTP ----
if [ $BOOT_SIG_TYPE == customer ]; then
	CUSTOMER_OTP_ARGS="`pwd`/key_hash1.bin `pwd`/key_hash2.bin"
fi

$WORKSPACE/FunSDK/bin/flash_tools/generate_otp.sh $CUSTOMER_OTP_ARGS

# Remove the MIF extension - these actually aren't in MIF format, and
# Rajesh's scripts for running jobs in emulation will do the needed
# conversions.
if [ $SECURE_BOOT == 'yes' ]; then
	cp OTP/OTP_memory_secure.mif ${WORKSPACE}/sbpimage/OTP_memory
else
	cp OTP/OTP_memory_unsecure.mif ${WORKSPACE}/sbpimage/OTP_memory
fi

cp -r ${WORKSPACE}/artifacts_$ARTIFACT_STYLE/ ${WORKSPACE}/sbpimage/archive

# copy bootloaders
cd $SBP_BUILD_DIR
find . -name "bootloader_m5150.*" -print | xargs tar cf - | (cd ${WORKSPACE}/sbpimage; tar xf -)

exit 0
