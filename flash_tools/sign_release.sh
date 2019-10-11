#!/bin/bash -e

function show_help()
{
    echo "sign_release.sh:  Create the NOR disk image with the proper keys and signatures from the HSM"
    echo ""
    echo "Usage:"
    echo "./sign_release.sh [key_label_suffix]"
    echo "key_label_suffix is the suffix identifying a key hierarchy"
    echo ""
    echo "NOTE: a start certificate must be present in the same directory as this script"
    echo ""
}


if [[ ( $@ == "--help") ||  $@ == "-h" ]] ; then
    show_help
    exit 0
fi

cd "$( dirname "${BASH_SOURCE[0]}" )"

# verify a start certificate was added to the directory...

if [ ! -f ./start_certificate.bin ]; then
    show_help
    echo "A start certificate file (start_certificate.bin) must be present in "`pwd`
    exit 1
fi

./release.py --action sign --with-hsm --sdkdir `pwd` --destdir `pwd` --key-name-suffix="$1" image.json
./release.py --action image --with-hsm --sdkdir `pwd` --destdir `pwd` image.json
