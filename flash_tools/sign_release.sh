#!/bin/bash -ex

cd "$( dirname "${BASH_SOURCE[0]}" )"

# verify a start certificate was added to the directory...

if [ ! -f ./start_certificate.bin ]; then
    echo "A start certificate file (start_certificate.bin) must be present in "`pwd`
    exit 1
fi

./release.py --action sign --with-hsm --sdkdir `pwd` --destdir `pwd` --key-name-suffix="$1" image.json
./release.py --action image --with-hsm --sdkdir `pwd` --destdir `pwd` image.json
