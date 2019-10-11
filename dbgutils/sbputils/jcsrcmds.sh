#! /bin/bash

TPOD=${1:-T4}

VIRTUALENV=/home/pmanjrekar/py2venv
pushd $(pwd) && cd $VIRTUALENV && source bin/activate && popd

set -x
python jcli.py --dut $TPOD --status
python jcli.py --dut $TPOD --otp
python jcli.py --dut $TPOD --cm-unlock --cm-cert fungible.cert  --cm-key fungible.pem --cm-grant 0x00080F80 --cm-pass fun123 --otp
#python jcli.py --dut $TPOD --csr
echo bye.
