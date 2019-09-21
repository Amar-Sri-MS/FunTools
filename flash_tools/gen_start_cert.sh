#!/bin/bash -ex

# generate the start certificate from the JSON specification file argument

cd "$( dirname "${BASH_SOURCE[0]}" )"

./release.py --action certificate --with-hsm --sdkdir `pwd` --destdir `pwd` $1
