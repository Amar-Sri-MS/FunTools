#!/usr/bin/env python3

import struct
import sys
import os
import configparser
import json
import argparse
import shutil
import generate_flash as gf


#TODO (make configurable for S1 and other)
HOST_FIRMWARE_CONFIG_OVERRIDE="""
{ "signed_images": {
     "host_firmware_packed_v1.bin": {
         "source":"u-boot.bin"
         }
     }
}
"""

#TODO (make configurable for S1 and other)
EEPROM_CONFIG_OVERRIDE="""
{ "signed_images": {
     "eeprom_packed_v1.bin": {
         "source":"eeprom_f1"
         }
     }
}
"""

def main():
    parser = argparse.ArgumentParser()
    flash_content = None
    config = {}

    parser.add_argument('config', nargs='+', help='Configuration file(s)')
    parser.add_argument('--action',
        choices={'all', 'prepare', 'sign', 'image'},
        default='all',
        help='Action to be performed on the input files')
    parser.add_argument('--sdkdir', required=True, help='SDK root directory')
    parser.add_argument('--destdir', required=True, help='Destination directory for output')

    args = parser.parse_args()

    wanted = lambda action : args.action in ['all', action]

    for config_file in args.config:
        if config_file == '-':
            gf.merge_configs(config, json.load(sys.stdin,encoding='ascii'))
        else:
            with open(config_file, 'r') as f:
                gf.merge_configs(config, json.load(f,encoding='ascii'))

    gf.merge_configs(config, json.loads(EEPROM_CONFIG_OVERRIDE))
    gf.merge_configs(config, json.loads(HOST_FIRMWARE_CONFIG_OVERRIDE))
    gf.set_config(config)

    if wanted('prepare'):
        # paths to application binaries in SDK tree
        paths = [ "bin",
                "FunSDK/u-boot",
                "FunSDK/sbpfw/roms",
                "FunSDK/sbpfw/eeproms",
                "FunSDK/sbpfw/firmware/chip_f1_emu_0",
                "FunSDK/sbpfw/pufrom/chip_f1_emu_0",
                ]
        sdkpaths = [os.path.join(args.sdkdir, path) for path in paths]

        # temporary as gf.run() doesn't support configurable target location
        if not os.path.exists(args.destdir):
            os.mkdir(args.destdir)
        os.chdir(args.destdir)
        gf.set_search_paths(sdkpaths)

        gf.run('sources')

    if wanted('sign'):
        sdkpaths = []
        sdkpaths.append(os.path.abspath(args.destdir))
        gf.set_search_paths(sdkpaths)
        gf.run('key_injection')
        gf.run('sign')

    if wanted('image'):
        sdkpaths = []
        sdkpaths.append(os.path.abspath(args.destdir))
        gf.set_search_paths(sdkpaths)
        gf.run('flash')


if __name__=="__main__":
    main()
