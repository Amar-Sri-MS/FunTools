#!/usr/bin/env bash
#
# Signing Server Configuration for Fungible SDK
#
# Copyright (c) 2021. Fungible, Inc.
# All rights reserved.

function show_help()
{
    echo "config_sdk_signing_server.sh: Set up Signing Server URL in SDK"
    echo ""
    echo "Arguments:"
    echo "-h, --help: show this message"
    echo "-C <path/to/sdk>: path to the Fungible SDK"
    echo "[SIGNING_SERVER_HTTP(S)_URL]"
    echo ""
    echo "Example: ./config_sdk_signing_server.sh http://localhost "
}

SDK_PATH="."
POSITIONAL=()

while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
	-C)
	   SDK_PATH="$2"
	    shift # past argument
	    shift # past value
	    ;;
	-h|--help)
	    show_help
	    exit 0
	    ;;
	-*)
	    echo "unknown option"
	    show_help
	    exit 0
	    ;;
	*)
	    POSITIONAL+=("$1") # save it in an array for later
	    shift # past argument
	    ;;
    esac
done

NUM_POSITIONAL=${#POSITIONAL[@]}

if [[ $NUM_POSITIONAL -eq 0 ]]; then
    show_help
    echo "***Error: missing URL"
    exit 0
fi

if [[ $NUM_POSITIONAL -gt 1 ]]; then
    show_help
    echo "***Error: specify only one URL"
    exit 0
fi

URL=${POSITIONAL[0]}

PREFIX="SIGNING_SERVER_URL = \""
REPLACE="$PREFIX""$URL""\""

if [[ $URL == http://* ]] || [[ $URL == https://* ]]; then
    NUM=`find "$SDK_PATH" -name firmware_signing_service.py \
	 -exec sed -i '.bak' 's|'"$PREFIX"'https*://.*$|'"$REPLACE"'|g' {} \;  \
	 -exec grep -c -e "$REPLACE" {} \;`
    echo "Replaced ""$NUM"" occurrence(s) to \""$URL"\""

else
    show_help
    echo "***Error: URL must start with http(s)://"
    exit 0
fi
