#!/usr/bin/env bash


function show_help()
{
    echo "$0: verify a start certificate"
    echo "Usage:"
    echo "$0 /path/to/public_key_file /path/to/certificate"
    echo ""
}

if [[ ( $@ == "--help") ||  $@ == "-h" ]] ; then
    show_help
    exit 0
fi

# arguments required
if [  $# != 2 ] ; then
    show_help
    echo "Missing argument(s)"
    exit 1
fi


dd if=$2 bs=1 count=580 | \
    openssl sha512 -verify $1 -signature <(dd if=$2 bs=1 skip=584)
