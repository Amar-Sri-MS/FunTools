#!/bin/bash

DEVTOOLS_DIR=$(readlink -f $WORKSPACE/SBPFirmware/software/devtools/firmware)

if [[ $# -ge 4 || $# -eq 0 ]]; then
    echo "Invalid number of keys hashes provided."
    echo "Usage: $0 <chip_name> [key_hash1] [key_hash2]"
    exit 1
fi

otp_hash_arg=""

CHIP_NAME=`echo "$1" | tr '[:lower:]' '[:upper:]'`

if [[ $# -ge 2 ]]; then
    otp_hash_arg="--key_hash1 $2"
fi
if [[ $# -ge 3 ]]; then
    otp_hash_arg+=" --key_hash2 $3"
fi

mkdir -p OTP

######################## OTP #################################
$DEVTOOLS_DIR/generate_otp.py \
        --cm_input $DEVTOOLS_DIR/otp_templates/OTP_content_CM.txt \
        --sm_input $DEVTOOLS_DIR/otp_templates/OTP_content_SM.txt \
        --ci_input $DEVTOOLS_DIR/otp_templates/OTP_content_CI_${CHIP_NAME}.txt \
        --unlocked $otp_hash_arg \
        --output OTP/OTP_memory_unlocked.mif

### generate the real ones : secure and unsecure  (with or without customer key)
for mode in secure unsecure; do
    $DEVTOOLS_DIR/generate_otp.py \
        --cm_input $DEVTOOLS_DIR/otp_templates/OTP_content_CM.txt \
        --sm_input $DEVTOOLS_DIR/otp_templates/OTP_content_SM.txt \
        --ci_input $DEVTOOLS_DIR/otp_templates/OTP_content_CI_${CHIP_NAME}.txt \
        --esecboot=$mode $otp_hash_arg \
        --output OTP/OTP_memory_$mode.mif
done
