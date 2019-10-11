#! /bin/bash

TPOD=${1:-T4}

VIRTUALENV=/home/pmanjrekar/py2venv
pushd $(pwd) && cd $VIRTUALENV && source bin/activate && popd

set -x
echo SBP get status ...
python jcli.py --dut $TPOD --status 
echo SBP get serial ...
python jcli.py --dut $TPOD --serial 
echo SBP test OTP grant bits ... expected to fail ...
python jcli.py --dut $TPOD --otp 
echo SBP test otp grant bits ... expected to pass ...
python jcli.py --dut $TPOD --cm-unlock --cm-cert fungible.cert  --cm-key fungible.pem --cm-grant 0x00080F00 --cm-pass fun123 --otp
echo SBP test flash grant bits ... expected to pass ...
python jcli.py --dut $TPOD --cm-unlock --cm-cert fungible.cert  --cm-key fungible.pem --cm-grant 0x00030F00 --cm-pass fun123 --flash 0
echo bye.
