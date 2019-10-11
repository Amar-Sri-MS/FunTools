#! /bin/bash

TPOD=${1:-T4}

VIRTUALENV=/home/pmanjrekar/py2venv
pushd $(pwd) && cd $VIRTUALENV && source bin/activate && popd

set -x
echo SBP get status ...
python icli.py --dut $TPOD --status 
echo SBP get serial ...
python icli.py --dut $TPOD --serial 
echo SBP test OTP grant bits ... expected to fail on secure chips ...
python icli.py --dut $TPOD --otp 
echo SBP test otp grant bits ... expected to pass ...
python icli.py --dut $TPOD --cm-unlock --cm-cert fungible.cert  --cm-key fungible.pem --cm-grant 0x00080E00 --cm-pass fun123 --otp
echo SBP test grant bits to call debug disconnect ... expected to fail ...
python icli.py --dut $TPOD --disconnect --otp
echo SBP test flash grant bits ... expected to pass ...
python icli.py --dut $TPOD --cm-unlock --cm-cert fungible.cert  --cm-key fungible.pem --cm-grant 0x00030F00 --cm-pass fun123 --flash 0
echo bye.
