#! /bin/bash

TPOD=${1:-T4}

VIRTUALENV=/home/pmanjrekar/py2venv
pushd $(pwd) && cd $VIRTUALENV && source bin/activate && popd

set -x
echo SBP get status ...
python icli.py --dut $TPOD --status 
echo SBP test - CSR access ... expected to fail on secure chips ...
python icli.py --dut $TPOD --csr
echo SBP test - CSR access after unlock ... should pass on secure chips ...
python icli.py --dut $TPOD --cm-unlock --cm-cert fungible.cert  --cm-key fungible.pem --cm-grant 0x00000F80 --cm-pass fun123 --csr
echo SBP test grant bits to call debug disconnect ... expected to fail ...
python icli.py --dut $TPOD --disconnect --csr
echo SBP test - CSR access after BAD unlock ... should fail on secure chips ...
python icli.py --dut $TPOD --cm-unlock --cm-cert fungible.cert  --cm-key fungible.pem --cm-grant 0x00000D00 --cm-pass fun123 --csr
echo SBP test - CSR access after GOOD bits ... should pass on secure chips ...
python icli.py --dut $TPOD --cm-unlock --cm-cert fungible.cert  --cm-key fungible.pem --cm-grant 0x00000F80 --cm-pass fun123 --csr
echo bye.
