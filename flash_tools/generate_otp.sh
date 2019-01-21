#!/bin/bash

FUNTOOLS_DIR=$(readlink -f `dirname $0`)
PRODUCTION_DIR=$(readlink -f $FUNTOOLS_DIR/../software/production)
DEVTOOLS_DIR=$(readlink -f $FUNTOOLS_DIR/../software/devtools/firmware)

if [[ $# -ge 3 ]]; then
    echo "Invalid number of keys hashes provided."
    echo "Usage: $0 [key_hash1] [key_hash2]"
    exit 1
fi

otp_hash_arg=""

if [[ $# -ge 1 ]]; then
    otp_hash_arg="--key_hash1 $1"
fi
if [[ $# -ge 2 ]]; then
    otp_hash_arg+=" --key_hash2 $2"
fi

mkdir -p OTP

######################## OTP #################################
python $DEVTOOLS_DIR/generate_otp.py \
        --cm_input $DEVTOOLS_DIR/otp_templates/OTP_content_CM.txt \
        --sm_input $DEVTOOLS_DIR/otp_templates/OTP_content_SM.txt \
        --ci_input $DEVTOOLS_DIR/otp_templates/OTP_content_CI.txt \
        --unlocked $otp_hash_arg \
        --output OTP/OTP_memory_unlocked.mif

### generate the real ones : secure and unsecure  (with or without customer key)
for mode in secure unsecure; do
    python $DEVTOOLS_DIR/generate_otp.py \
        --cm_input $DEVTOOLS_DIR/otp_templates/OTP_content_CM.txt \
        --sm_input $DEVTOOLS_DIR/otp_templates/OTP_content_SM.txt \
        --ci_input $DEVTOOLS_DIR/otp_templates/OTP_content_CI.txt \
        --esecboot=$mode $otp_hash_arg \
        --output OTP/OTP_memory_$mode.mif
done
