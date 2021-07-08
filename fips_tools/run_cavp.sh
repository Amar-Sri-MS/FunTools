#! /bin/bash -ex

function show_help()
{
    echo "run_cavp.sh: run a cavp test"
    echo "Usage:"
    echo "./run_cavp.sh <options> <files>"
    echo "Examples:"
    echo "./run_cavp.sh acumen_21_03_31/SBP/request/SBP_Request_SHA-1_515778.req.json"
    echo "./run_cavp.sh -s SBP acumen_21_03_31/SBP/request/SBP_Request_ACVP-AES-GCM_515793.req.json"
}

if [[ ( $@ == "--help") ||  $@ == "-h" ]] ; then
    show_help
    exit 0
fi

# file argument(s) required
if [  $# == 0 ] ; then
    show_help
    echo "Missing argument: file(s)"
    exit 1
fi

sed "s|<description>|$(basename ${*: -1})|g" cavp_test.params > cavp_test_filled.params
echo ' ' $* >> cavp_test_filled.params
./run_f1.py --rootfs-image ../fod/rootfs-images/ --params ../fod/cavp_test_filled.params funos-f1.signed  2>&1
echo "    Done!"
