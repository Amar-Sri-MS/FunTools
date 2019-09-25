#!/bin/bash -e

# generate the start certificate from the JSON specification file argument

function show_help()
{
    echo "gen_start_cert.sh:  Generate (Sign) a start certificate according to a JSON specification"
    echo ""
    echo "Usage:"
    echo "./gen_start_cert.sh json_specification_file"
    echo ""
    echo "INFO: The json specification file for a start certificate can be generated using the SerialNumbers Google Sheet"
    echo ""
}


if [[ ( $@ == "--help") ||  $@ == "-h" ]] ; then
    show_help
    exit 0
fi

# JSON specification argument required
if [  $# != 1 ] ; then
    show_help
    echo "Argument missing: JSON specification file"
    exit 1
fi

cd "$( dirname "${BASH_SOURCE[0]}" )"

./release.py --action certificate --with-hsm --sdkdir `pwd` --destdir `pwd` $1
