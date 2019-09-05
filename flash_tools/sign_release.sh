#!/bin/bash -ex
cd ${WORKSPACE}/TO_BE_SIGNED

./release.py --action sign --with-hsm --sdkdir `pwd` --destdir `pwd` image.json
./release.py --action image --with-hsm --sdkdir `pwd` --destdir `pwd` image.json
