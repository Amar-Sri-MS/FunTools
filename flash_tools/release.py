#!/usr/bin/env python3

'''
Copyright (c) 2019-2020 Fungible, inc.
All Rights Reserved.
'''

import struct
import sys
import os
import configparser
import glob
import json
import argparse
import shutil
import subprocess
import tarfile
import tempfile
import generate_flash as gf
import flash_utils
import eeprom_replace as er
import os_utils


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
         "source":"eeprom_f1_dev_board"
         }
     }
}
"""

FUNOS_CONFIG_OVERRIDE="""
{{ "signed_images": {{
     "funos.signed.bin": {{
         "source":"{funos_appname}"
         }}
     }}
}}
"""

EEPROM_LIST_CONFIG_OVERRIDE="""
{{ "signed_images": {{
     "eeprom_list": {{
         "source":"@file:{eeprom_list}"
         }}
     }}
}}
"""

FVHT_LIST_CONFIG_OVERRIDE="""
{{ "signed_images": {{
     "FVHT": {{
       "source": "@file:{fvht_list}"
        }}
    }}
}}
"""

# TODO this should be autogenerated by bob when building the sdk
ALL_ROOTFS_FILES = {
    "f1" : [ 'fs1600-rootfs-ro.squashfs' ],
    "s1" : [ 's1-rootfs-ro.squashfs' ],
    "f1d1" : [ 'fs1600-rootfs-ro.squashfs' ]
}

CHIP_SPECIFIC_FILES = {
    "s1" : [ 'fdc_cbs/composer-boot-services-emmc.img' ]
}

def _rootfs(f, rootfs):
    return '{}.{}'.format(rootfs, f)

def _mfg(f, signed=False):
    if signed:
        return '{}.{}.{}'.format(f, 'mfginstall','signed')
    else:
        return '{}.{}'.format(f, 'mfginstall')

def _nor(f, signed=False):
    if signed:
        return '{}.{}.{}'.format(f, 'norinstall','signed')
    else:
        return '{}.{}'.format(f, 'norinstall')

def main():
    parser = argparse.ArgumentParser()
    config = {}

    parser.add_argument('config', nargs='*', help='Configuration file(s)')
    parser.add_argument('--action',
        choices={'all', 'prepare', 'sdk-prepare', 'release', 'sdk-release', 'certificate', 'sign', 'image', 'tarball', 'bundle', 'eeprbundle', 'mfginstall', 'mfgtarball'},
        default='all',
        help='Action to be performed on the input files')
    parser.add_argument('--sdkdir', default=os.getcwd(), help='SDK root directory')
    parser.add_argument('--destdir', default='RELEASE', help='Destination directory for output')
    parser.add_argument('--force-version', type=int, help='Override firmware versions')
    parser.add_argument('--force-description', help='Override firmware description strings')
    parser.add_argument('--chip', choices=['f1', 's1', 'f1d1'], default='f1', help='Target chip')
    parser.add_argument('--debug-build', dest='release', action='store_false', help='Use debug application binary')
    parser.add_argument('--default-config-files', dest='default_cfg', action='store_true')
    parser.add_argument('--dev-image', action='store_true', help='Create a development image installer')

    args = parser.parse_args()

    if args.default_cfg == False and len(args.config) == 0:
        parser.error("One of '--default-config-files' or a list of config files is required")

    funos_suffixes = ['', args.chip]
    if args.release:
        funos_suffixes.append('release')

    args.sdkdir = os.path.abspath(args.sdkdir) # later processing fails if relative path is given
    funos_appname = "funos{}.stripped".format('-'.join(funos_suffixes))
    rootfs_files = ALL_ROOTFS_FILES[args.chip]
    chip_specific_files = CHIP_SPECIFIC_FILES.get(args.chip, ())

    def wanted(action):
        if args.action == 'all':
            return True
        elif args.action == 'release':
            return action in ['sign', 'image', 'tarball', 'bundle', 'eeprbundle', 'mfginstall', 'mfgtarball']
        elif args.action == 'sdk-release':
            return action in ['funos_loader', 'sign', 'image', 'bundle']
        else:
            return action == args.action

    if args.default_cfg:
        if wanted('prepare') or wanted('sdk-prepare'):
            args.config = [
                'bin/flash_tools/qspi_config_fungible.json',
                'bin/flash_tools/mmc_config_fungible.json',
                'bin/flash_tools/key_bag_config.json',
                'FunSDK/nvdimm_fw/nvdimm_fw_config.json' ]
        else:
            args.config = [ 'image.json' ]

    for config_file in args.config:
        if config_file == '-':
            gf.merge_configs(config, json.load(sys.stdin))
        else:
            with open(config_file, 'r') as f:
                gf.merge_configs(config, json.load(f))

    eeprom_list = '{}_eeprom_list.json'.format(args.chip)
    fvht_list_file = None

    if wanted('prepare') or wanted('sdk-prepare'):
        gf.merge_configs(config, json.loads(EEPROM_CONFIG_OVERRIDE), only_if_present=True)
        gf.merge_configs(config, json.loads(HOST_FIRMWARE_CONFIG_OVERRIDE), only_if_present=True)
        gf.merge_configs(config, json.loads(FUNOS_CONFIG_OVERRIDE.format(funos_appname=funos_appname)), only_if_present=True)
        gf.merge_configs(config, json.loads(EEPROM_LIST_CONFIG_OVERRIDE.format(eeprom_list=eeprom_list)), only_if_present=True)

        fvht_config = {}
        fvht_list_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        for rootfs in rootfs_files:
            fvht_config[rootfs] = {
                'filename' : _rootfs('fvht.unsigned', rootfs),
                'target' : _rootfs('fvht.signed', rootfs)
            }
        json.dump(fvht_config, fvht_list_file)
        fvht_list_file.flush()
        fvht_override = json.loads(FVHT_LIST_CONFIG_OVERRIDE.format(fvht_list=fvht_list_file.name))
        if config['signed_images'].get(list(fvht_override['signed_images'].keys())[0]):
            gf.merge_configs(config, fvht_override)

    gf.set_config(config)
    gf.set_chip_type(args.chip)

    if args.dev_image:
        if config.get('global_config'):
            config['global_config'].update({'dev_image':True})
        else:
            config['global_config'] = {'dev_image':True}
    else:
        # if --dev-image was not specified in cmdline args check
        # if config.json:/global_config/dev_image exists
        if config.get('global_config'):
            config_dev_image = config['global_config'].get('dev_image')
            if config_dev_image:
                args.dev_image = True

    if args.force_version:
        gf.set_versions(args.force_version)

    if args.force_description:
        gf.set_description(args.force_description, True)

    curdir = os.getcwd()

    if wanted('prepare') or wanted('sdk-prepare'):
        # paths to application binaries in SDK tree
        paths = [ "bin",
                "FunSDK/sbpfw/roms",
                "FunSDK/sbpfw/eeproms",
                "FunSDK/nvdimm_fw",
                "feature_sets",
                ]
        sdkpaths = [os.path.join(args.sdkdir, path) for path in paths]

        paths_chip_specific = [ "FunSDK/u-boot/{chip}",
                "FunSDK/sbpfw/firmware/chip_{chip}_emu_0",
                "FunSDK/sbpfw/pufrom/chip_{chip}_emu_0",
                ]
        sdkpaths.extend(
            [os.path.join(args.sdkdir, path.format(chip=args.chip)) for path in paths_chip_specific])

        # temporary as gf.run() doesn't support configurable target location
        if not os.path.exists(args.destdir):
            os.makedirs(args.destdir)
        os.chdir(args.destdir)
        gf.set_search_paths(sdkpaths)

        gf.run('sources')

        utils = [ "bin/flash_tools/generate_flash.py",
                  "bin/flash_tools/make_emulation_emmc.py",
                  "bin/flash_tools/firmware_signing_service.py",
                  "bin/flash_tools/key_bag_create.py",
                  "bin/flash_tools/key_replace.py",
                  "bin/flash_tools/eeprom_replace.py",
                  "bin/flash_tools/flash_utils.py",
                  "bin/flash_tools/gen_hash_tree.py",
                  "bin/flash_tools/os_utils.py",
                  "bin/flash_tools/" + os.path.basename(__file__),
                  "bin/Linux/x86_64/mkimage",
                  "bin/scripts/gen_fgpt.py",
                  "bin/scripts/xdata.py" ]
        utils.append(os.path.join('FunSDK/sbpfw/eeproms', eeprom_list))

        for app in utils:
            shutil.copy2(os.path.join(args.sdkdir, app), os.path.basename(app))

        shutil.rmtree('install_tools', ignore_errors=True)
        shutil.copytree(os.path.join(args.sdkdir, 'bin/flash_tools/install_tools'),
            'install_tools')
        for rootfs in rootfs_files:
            root_file = os.path.join(args.sdkdir, 'deployments', rootfs)
            shutil.copy2(root_file, rootfs)
            try:
                shutil.copy2(root_file + '.version', rootfs + '.version')
            except FileNotFoundError:
                pass

        if wanted('prepare'):
            # these files are not needed in sdk-prepare
            shutil.copy2(funos_appname, funos_appname + ".mfginstall")
            shutil.copy2(funos_appname, funos_appname + ".norinstall")

            for chip_file in chip_specific_files:
                shutil.copy2(os.path.join(args.sdkdir, chip_file), os.path.basename(chip_file))

        bld_info = os.path.join(args.sdkdir, 'build_info.txt')
        v = args.force_version
        sdk_v = v

        if os.path.exists(bld_info):
            with open(bld_info, 'r') as f:
                sdk_v = int(eval(f.readline()))
                if not args.force_version:
                    v = sdk_v
                    gf.set_versions(v)

        with open('.version', 'w') as version_file:
            version_file.write('funsdk={}\n'.format(v))
            version_file.write('funsdk_version={}\n'.format(sdk_v))

        if not wanted('sdk-prepare'):
            # in sdk builds, the bootscript will need to be
            # generated later when a new funos image is present
            cmd = [ 'python', 'make_emulation_emmc.py',
                    '-w', '.',
                    '-o', '.',
                    '--appfile', funos_appname,
                    '--filesystem',
                    '--signed',
                    '--bootscript-only']
            subprocess.check_call(cmd)

        if not args.dev_image:
            # dev images do not need cclinux stuff
            cmd = [ 'python3', 'gen_fgpt.py', 'fgpt.unsigned' ]
            subprocess.call(cmd)

            cmd = [ 'python3', 'xdata.py',
                    '-r',
                    '--data-offset=4096',
                    '--data-alignment=512',
                    '--padding=4',
                    'fvos.unsigned',
                    'add',
                    os.path.join(args.sdkdir,
                        'bin/cc-linux-yocto/mips64hv/vmlinux.bin') ]
            subprocess.call(cmd)

            for rootfs in rootfs_files:
                cmd = [ 'python3', 'gen_hash_tree.py',
                        '-O', _rootfs('fvht.bin', rootfs),
                        'hash',
                        '-N', 'rootfs.hashtree',
                        '--to-sign', _rootfs('fvht.unsigned', rootfs),
                        '-I', rootfs ]
                subprocess.call(cmd)

        with open("image.json", "w") as f:
            json.dump(config, f, indent=4)

        os.unlink(fvht_list_file.name)
        os.chdir(curdir)

    if wanted('certificate'):
        sdkpaths = []
        sdkpaths.append(os.path.abspath(args.destdir))
        gf.set_search_paths(sdkpaths)
        os.chdir(args.destdir)
        gf.run('certificates')
        os.chdir(curdir)

    if wanted('funos_loader'):
        # if funos image is different then create a new bootloader script
        os.chdir(args.destdir)
        cmd = [ 'python', 'make_emulation_emmc.py',
                '-w', '.',
                '-o', '.',
                '--appfile', funos_appname,
                '--filesystem',
                '--signed',
                '--bootscript-only']
        subprocess.check_call(cmd)
        os.chdir(curdir)

    if wanted('sign'):
        sdkpaths = []
        sdkpaths.append(os.path.abspath(args.destdir))
        gf.set_search_paths(sdkpaths)
        os.chdir(args.destdir)
        gf.run('key_injection', keep_output=True)
        gf.run('certificates')
        gf.run('sign')
        os.chdir(curdir)

    if wanted('image'):
        sdkpaths = []
        sdkpaths.append(os.path.abspath(args.destdir))
        gf.set_search_paths(sdkpaths)
        os.chdir(args.destdir)
        gf.run('flash')

        cmd = [ 'python', 'make_emulation_emmc.py',
                '-w', '.',
                '-o', '.',
                '--appfile', 'funos.signed.bin',
                '--fsfile', 'boot.img.signed',
                '--filesystem',
                '--signed' ]
        subprocess.check_call(cmd)

        for rootfs in rootfs_files:
            cmd = [ 'python3', 'gen_hash_tree.py',
                    '-O', _rootfs('fvht.bin', rootfs),
                    'insert',
                    '--signed', _rootfs('fvht.signed', rootfs) ]
            subprocess.call(cmd)

        try:
            output_image = config['output_format']['output']
            with open(eeprom_list) as f:
                eeproms = json.load(f)
                for skuid, value in eeproms.items():
                    er.replace('{}.bin'.format(output_image),
                        '{}.bin.{}'.format(output_image, skuid), value['filename'] + '.bin')
        except:
            pass

        os.chdir(curdir)

    if wanted('tarball'):
        os.chdir(args.destdir)
        tarfiles = []

        with open("image.json") as f:
            images = json.load(f)
            tarfiles.extend([key for key,value in images['signed_images'].items()
                                if not value.get("no_export", False)])
            tarfiles.extend([key for key,value in images['signed_meta_images'].items()
                                if not value.get("no_export", False)])

        with open("mmc_image.json") as f:
            images = json.load(f)
            tarfiles.extend([key for key,value in images['generated_images'].items()
                                if not value.get("no_export", False)])

        tarfiles.append('image.json')
        tarfiles.append('mmc_image.json')
        for rootfs in rootfs_files:
            tarfiles.append(_rootfs('fvht.bin', rootfs))
            tarfiles.append(rootfs)
        tarfiles.extend(glob.glob('qspi_image_hw.bin.*'))

        for chip_file in chip_specific_files:
            tarfiles.append(os.path.basename(chip_file))

        if os.path.exists('.version'):
            tarfiles.append('.version')

        with tarfile.open('{chip}_sdk_signed_release.tgz'.format(chip=args.chip), mode='w:gz') as tar:
            for f in tarfiles:
                tar.add(f)

        os.chdir(curdir)

    if wanted('bundle'):
        os.chdir(args.destdir)
        for rootfs in rootfs_files:
            shutil.rmtree('bundle_installer', ignore_errors=True)
            os.mkdir('bundle_installer')
            bundle_images = []

            with open("image.json") as f:
                images = json.load(f)
                bundle_images.extend([key for key,value in images.get('signed_images',{}).items()
                                    if not value.get("no_export", False)])
                bundle_images.extend([key for key,value in images.get('signed_meta_images', {}).items()
                                    if not value.get("no_export", False)])

            with open("mmc_image.json") as f:
                images = json.load(f)
                bundle_images.extend([key for key,value in images.get('generated_images',{}).items()
                                    if not value.get("no_export", False)])

            bundle_images.extend([
                'install_tools/run_fwupgrade.py',
                'install_tools/setup.sh',
                'image.json'
            ])

            if not args.dev_image:
                bundle_images.extend([
                    _rootfs('fvht.bin', rootfs),
                    rootfs
                ])

            for chip_file in chip_specific_files:
                bundle_images.append(os.path.basename(chip_file))

            if os.path.exists('.version'):
                bundle_images.append('.version')

            if os.path.exists(rootfs + '.version'):
                bundle_images.append(rootfs + '.version')

            for f in bundle_images:
                os.symlink(os.path.join(os.path.abspath(os.curdir), f), os.path.join('bundle_installer', os.path.basename(f)))

            with open(os.path.join('bundle_installer', '.setup'), "w") as cfg:
                cfg.writelines([
                    'ROOTFS_NAME="{}"\n'.format(rootfs),
                    'CHIP_NAME="{}"\n'.format(args.chip.upper()),
                    'DEV_IMAGE={}\n'.format(1 if args.dev_image else 0)
                ])

            bundle_name = 'development_image' if args.dev_image else rootfs
            makeself = [
                os_utils.path_fixup('makeself'),
                '--follow',
                'bundle_installer',
                'setup_bundle_{}.sh'.format(bundle_name),
                'CCLinux/FunOS {} installer'.format(bundle_name),
                './setup.sh'
            ]

            subprocess.call(makeself)

        os.chdir(curdir)

    if wanted('eeprbundle'):
        os.chdir(args.destdir)
        with open(eeprom_list) as f:
            eeproms = json.load(f)
            for skuid, value in eeproms.items():
                if not value.get('hw_base'):
                    continue

                shutil.rmtree('eepr_installer', ignore_errors=True)
                os.mkdir('eepr_installer')

                bundle_images = [
                    'install_tools/run_fwupgrade.py',
                    'install_tools/setup_eepr.sh',
                    'image.json',
                    '{}.bin'.format(value['filename'])
                ]

                for f in bundle_images:
                    os.symlink(os.path.join(os.path.abspath(os.curdir), f),
                               os.path.join('eepr_installer', os.path.basename(f)))

                with open(os.path.join('eepr_installer', '.setup'), "w") as cfg:
                    cfg.writelines([
                        'EEPR_NAME="{}"\n'.format(skuid),
                        'CHIP_NAME="{}"\n'.format(args.chip.upper()),
                        'HW_BASE="{}"\n'.format(value['hw_base'].upper())
                    ])

                makeself = [
                    os_utils.path_fixup('makeself'),
                    '--follow',
                    'eepr_installer',
                    'setup_bundle_eepr_{}_{}.sh'.format(args.chip.lower(), skuid),
                    'DPU EEPR {} installer'.format(skuid),
                    './setup_eepr.sh'
                ]

                subprocess.call(makeself)
        os.chdir(curdir)

    if wanted('mfginstall'):
        os.chdir(args.destdir)

        rootfs = rootfs_files[0]
        mfgxdata = {
            'husc' : ('nor', 'hu_sbm_serdes.bin'),
            'hbsb' : ('nor', 'hbm_sbus.bin'),
            'kbag' : ('nor', 'key_bag.bin'),
            'host' : ('nor', 'host_firmware_packed.bin'),
            'sbpf' : ('nor', 'esecure_firmware_all.bin'),
            'fgpt' : ('mmc', 'fgpt.signed'),
            'fvp1' : ('mmc', 'fvos.signed'),
            'fvp2' : ('mmc', rootfs),
            'fvp4' : ('mmc', _rootfs('fvht.bin', rootfs)),
            'emmc' : ('mmc', 'emmc_image.bin'),
        }

        # that's a bit hacky ... need something better here
        if args.chip == 'f1':
            mfgxdata['ccfg'] = ('mmc', 'ccfg-no-come.signed.bin')
        elif args.chip == 's1':
            mfgxdata['ccfg'] = ('mmc', 'ccfg-s1-demo-10g_mpg.signed.bin')
            mfgxdata['dcc0'] = ('mmc', 'composer-boot-services-emmc.img')

        mfgxdata_lists = {
            'fw_upgrade_all': 'all',
            'fw_upgrade_nor': 'nor',
            'fw_upgrade_mmc': 'mmc'
        }

        for fname, target in mfgxdata_lists.items():
            # generate upgrade lists to be embedded in xdata
            with open(fname, 'w') as f:
                for key, (imgtarget, imgfile) in mfgxdata.items():
                    if target == imgtarget or target == 'all':
                        f.write("{}\n".format(key))

        def _gen_xdata_funos(outname_modifier, target=None):
            with open('fw_upgrade_xdata', 'w') as f:
                # generate complete xdata list
                for key, (imgtarget, imgfile) in mfgxdata.items():
                    if not target or imgtarget == target:
                        f.write("{} {}\n".format(key, os.path.join(os.getcwd(), imgfile)))

                for fname in mfgxdata_lists:
                    f.write("{} {}\n".format(fname, os.path.join(os.getcwd(), fname)))

            cmd = [ 'python3', 'xdata.py',
                    outname_modifier(funos_appname),
                    'add-file-lists',
                    'fw_upgrade_xdata' ]
            subprocess.call(cmd)

        _gen_xdata_funos(_mfg)
        _gen_xdata_funos(_nor, 'nor')

        # take a copy of all funos default settings for signing
        # and only override filenames used
        mfg_app_config = config['signed_images'].get('funos.signed.bin').copy()
        mfg_app_config['source'] = _mfg(funos_appname)
        config['signed_mfg_images'] = {
            _mfg(funos_appname, signed=True) : mfg_app_config
        }
        gf.set_search_paths([os.getcwd()])
        gf.create_file(_mfg(funos_appname, signed=True), section='signed_mfg_images')

        mfg_app_config['source'] = _nor(funos_appname)
        config['signed_mfg_images'] = {
            _nor(funos_appname, signed=True) : mfg_app_config
        }
        gf.set_search_paths([os.getcwd()])
        gf.create_file(_nor(funos_appname, signed=True), section='signed_mfg_images')

        os.chdir(curdir)

    if wanted('mfgtarball'):
        os.chdir(args.destdir)
        tarfiles = []

        tarfiles.extend(glob.glob('qspi_image_hw.bin.*'))
        tarfiles.append(_mfg(funos_appname, signed=True))

        if os.path.exists('.version'):
            tarfiles.append('.version')

        with tarfile.open('{chip}_mfg_package.tgz'.format(chip=args.chip), mode='w:gz') as tar:
            for f in tarfiles:
                tar.add(f)

        os.chdir(curdir)


if __name__=="__main__":
    main()
