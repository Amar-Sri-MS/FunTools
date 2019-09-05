#!/usr/bin/env python3

import struct
import sys
import os
import configparser
import json
import argparse
import shutil
import subprocess
import generate_flash as gf
import flash_utils


#TODO (make configurable for S1 and other)
HOST_FIRMWARE_CONFIG_OVERRIDE="""
{ "signed_images": {
     "host_firmware_packed.bin": {
         "source":"u-boot.bin"
         }
     }
}
"""

#TODO (make configurable for S1 and other)
EEPROM_CONFIG_OVERRIDE="""
{ "signed_images": {
     "eeprom_packed.bin": {
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
    parser.add_argument('--force-version', type=int, help='Override firmware versions')
    parser.add_argument('--force-description', help='Override firmware description strings')
    parser.add_argument('--with-hsm', action='store_true', help='Use HSM for signing')
    group_fs1600 = parser.add_mutually_exclusive_group()
    group_fs1600.add_argument('--generate-fs1600', dest='fs1600', action='store_const', const=1, help='Generate FS1600 flash images')
    group_fs1600.add_argument('--generate-fs1600r2', dest='fs1600', action='store_const', const=2, help='Generate FS1600r2 flash images')

    args = parser.parse_args()

    use_hsm = args.with_hsm
    use_net = not use_hsm

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

    if args.force_version:
        gf.set_versions(args.force_version)

    if args.force_description:
        gf.set_description(args.force_description, True)

    curdir = os.getcwd()

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

        utils = [ "bin/flash_tools/generate_firmware_image.py",
                  "bin/flash_tools/generate_flash.py",
                  "bin/flash_tools/make_emulation_emmc.py",
                  "bin/flash_tools/firmware_signing_service.py",
                  "bin/flash_tools/enrollment_service.py",
                  "bin/flash_tools/key_replace.py",
                  "bin/flash_tools/flash_utils.py",
                  "bin/flash_tools/sign_release.sh",
                  "bin/flash_tools/" + os.path.basename(__file__),
                  "bin/Linux/x86_64/mkimage" ]
        for app in utils:
            shutil.copy2(os.path.join(args.sdkdir, app), os.path.basename(app))

        #TODO(mnowakowski)
        #     skip direct invocation and import make_emulation_emmc
        cmd = [ 'python', 'make_emulation_emmc.py',
                '-w', '.',
                '-o', '.',
                '--appfile', 'funos-f1.stripped',
                '--filesystem',
                '--signed',
                '--bootscript-only']
        subprocess.call(cmd)

        with open("image.json", "w") as f:
            json.dump(config, f, indent=4)

        gf.run('key_injection', net=use_net, hsm=use_hsm)
        os.chdir(curdir)

    if wanted('sign'):
        sdkpaths = []
        sdkpaths.append(os.path.abspath(args.destdir))
        gf.set_search_paths(sdkpaths)
        os.chdir(args.destdir)
        gf.run('key_injection', net=use_net, hsm=use_hsm, keep_output=True)
        gf.run('certificates', net=use_net, hsm=use_hsm)
        gf.run('sign', net=use_net, hsm=use_hsm)
        os.chdir(curdir)


    if wanted('image'):
        sdkpaths = []
        sdkpaths.append(os.path.abspath(args.destdir))
        gf.set_search_paths(sdkpaths)
        os.chdir(args.destdir)
        gf.run('flash')

        if args.fs1600:
            image_base = config['output_format']['output']
            image = image_base + '.bin'
            parts = list(filter(lambda f: f[0] == 'eepr', flash_utils.get_entries(image)))
            eeprlist = ()
            if args.fs1600 == 1:
                eeprlist = ('fs1600_0', 'fs1600_1')
            elif args.fs1600 == 2:
                eeprlist = ('fs1600r2_0', 'fs1600r2_1')

            for e in eeprlist:
                destfile = image_base + '_' + e + '.bin'
                shutil.copy2(image, destfile)
                for p in parts:
                    cmd = ['dd',
                           'if=eeprom_{}_packed.bin'.format(e),
                           'of={}'.format(destfile),
                           'conv=notrunc',
                           'obs=1',
                           'seek={}'.format(p[1])]
                    subprocess.call(cmd)



        #TODO(mnowakowski)
        #     skip direct invocation and import make_emulation_emmc
        cmd = [ 'python', 'make_emulation_emmc.py',
                '-w', '.',
                '-o', '.',
                '--appfile', 'funos.signed.bin',
                '--fsfile', 'boot.img.signed',
                '--filesystem',
                '--signed' ]
        subprocess.call(cmd)

        os.chdir(curdir)

if __name__=="__main__":
    main()
