#!/usr/bin/env bash
#
# Generate a new key and CSR for ESRP
#
# Copyright (c) 2024. Microsoft Corporation
#



KEYFILE=${1:-esrp_csr.key}
CSRFILE=${2:-esrp_csr.csr}

openssl req -new -config $(dirname "$0")/openssl.conf -sha256 -newkey rsa:2048 \
	-keyout "${KEYFILE}" -out "${CSRFILE}"
