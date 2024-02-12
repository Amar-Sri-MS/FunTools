#!/usr/bin/env python3
##
##  Copyright (C) 2017 Fungible. All rights reserved.
##

import argparse
import base64
import json
import os
import subprocess
import time

import dpc_client

ENV_BLOB_SIZE = 0x1000

def get_host_data(dpc, args):
    resp = dpc.execute('uboot', ['get_env_data', {'size':ENV_BLOB_SIZE}])
    if not resp:
        raise Exception('FunOS returned error, this might be because of outdated firmware')

    data = resp.get('data_b64')
    if not resp:
        raise Exception('Malformed FunOS response, data not found')

    data_raw = base64.b64decode(data, validate=True)
    with open(args.config_file, 'wb') as f:
        f.write(data_raw)

def set_host_data(dpc, args):
    with open(args.config_file, 'rb') as f:
        data = f.read()

    if len(data) != ENV_BLOB_SIZE:
        raise Exception('Invalid config file size')

    if any(data[ENV_BLOB_SIZE//2:]):
        # uboot is limited to only support a few variables in flash
        # and dpcsh nvme transport implementation is currently limited
        # to sending only a max cmd size of 4k, so we're expecting most
        # of the env file to be nulls that can be stripped before sending
        raise Exception('Too many config entries')

    data_enc = base64.b64encode(data[:ENV_BLOB_SIZE//2]).decode('ascii')

    resp = dpc.execute('uboot', ['set_env_data', {'data_b64':data_enc}])
    if not resp:
        raise Exception('FunOS returned error, this might be because of outdated firmware')


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('action', choices=['get', 'set'], help='Action to perform')
    parser.add_argument('--config-file', default='/tmp/uboot_sbp.env',
                        help='Local file to store/read copy of u-boot environment')
    parser.add_argument('--dpc-socket', required=True,
                        help='Unix socket of dpcsh')

    args = parser.parse_args()

    try:
        dpc = dpc_client.DpcClient(unix_sock=True, server_address = args.dpc_socket)
        if args.action == 'get':
            get_host_data(dpc, args)
        elif args.action == 'set':
            set_host_data(dpc, args)
    except Exception as e:
        print("Command failed, error:{}".format(e))
        raise

    return 0

if __name__=="__main__":
    main()
