#!/bin/bash

PRODUCTION_DIR="${PRODUCTION_DIR:-$WORKSPACE/SBPFirmware/software/production}"
FUNSDK_BIN_DIR="${FUNSDK_BIN_DIR:-$WORKSPACE/FunSDK/bin}"

# This function imports the development key into the (Soft)HSM so that it can be
# used to sign other binaries. It first verifies that the key matches the one in
# the start certificate.
function import_development_key() {

    PUB_KEY_OFFSET=68
    PUB_KEY_LEN=256

    local CERTIFICATE=$1
    local OSSL_KEY=$2

    if diff -q  <(openssl rsa -in $OSSL_KEY -modulus 2>/dev/null | cut -f 2 -d '=' -s | xxd -p -r  -) \
        <(dd if=$CERTIFICATE skip=$PUB_KEY_OFFSET count=$PUB_KEY_LEN bs=1 2>/dev/null) ; then
    python3 $FUNSDK_BIN_DIR/flash_tools/generate_firmware_image.py import -k fpk2 -r $OSSL_KEY
    else
    echo "certificate and key have different modulus"
    return 1
    fi
}

####################### CERTIFICATE ##########################
if [ -f $PRODUCTION_DIR/fpk1_modulus.c ]; then
    # THERE MUST BE A START CERTIFICATE signed with the production FPK1 and its KEY
    echo "fpk1_modulus.c found in $PRODUCTION_DIR: using start_certificate signed with production key"
    cp $PRODUCTION_DIR/development_start_certificate.bin ./start_certificate.bin
    # import the development FPK2 key if any into the (Soft)HSM
    if [ -f $PRODUCTION_DIR/development_fpk2.pem ]; then
    import_development_key \
        $PRODUCTION_DIR/development_start_certificate.bin \
        $PRODUCTION_DIR/development_fpk2.pem
    fi
fi
