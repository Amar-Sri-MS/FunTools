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
         "source":"eeprom_f1_f1_dev_board"
         }
     }
}
"""

# These are dummy filler configs. Upgrade script picks the right one based on the sku
BOARD_CFG_PER_CHIP_SKU_DEFAULT = {
	"f1": "f1_dev_board",
	"f1d1": "fs800v2",
	"s1": "fc50",
	"s2": "ds400"
}

BOARD_CONFIG_OVERRIDE="""
{{ "signed_images": {{
     "board_cfg.bin": {{
         "source":"boardcfg_{sku_name}_default"
         }}
     }}
}}
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

BOARD_CFG_LIST_CONFIG_OVERRIDE="""
{{ "signed_images": {{
     "board_cfg_list": {{
         "source":"@file:{board_cfg_list}"
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

CSRR_CONFIG_OVERRIDE="""
{{ "signed_images": {{
     "csr_override.bjson.signed": {{
       "source": "csr_override_{chip}.bjson"
        }}
    }}
}}
"""


def localdir(fname):
    return "./" + fname

# TODO this should be autogenerated by bob when building the sdk
ALL_ROOTFS_FILES = {
    # each entry is a list of tuples (rootfs-name, release bundle name) to generate
    # Currently release bundle name is always the same as the chip,
    # but they are set explicitly as we might be generating mutliple bundles
    # per DPU, so a dpu name would not be enough to distinguish various
    # bundle types
    "f1" : [ ('fs1600-rootfs-ro.squashfs', 'f1') ],
    "s1" : [ ('s1-rootfs-ro.squashfs', 's1') ],
    "f1d1" : [ ('fs1600-rootfs-ro.squashfs', 'f1d1') ],
    "s2" : [ (None, 's2')]
}

CHIP_SPECIFIC_FILES = {
    # none right now
}

CHIP_WITH_FUNVISOR = [ 'f1', 'f1d1', 's1' ]

def _rootfs(f, rootfs):
    return '{}.{}'.format(rootfs, f)

def _mfgfilename(f, name, signed=False):
    if signed:
        return '{}.{}'.format(f, name)
    else:
        return '{}.{}.{}'.format(f, name, 'unsigned')

def _mfg(f, signed=False):
    return _mfgfilename(f, 'mfginstall', signed)

def _mfgnofv(f, signed=False):
    return _mfgfilename(f, 'nofv.mfginstall', signed)

def _nor(f, signed=False):
    return _mfgfilename(f, 'norinstall', signed)

def _want_funvisor(args):
    return args.funvisor or args.dev_image


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
    parser.add_argument('--chip', choices=['f1', 's1', 'f1d1', 's2'], default='f1', help='Target chip')
    parser.add_argument('--debug-build', dest='release', action='store_false', help='Use debug application binary')
    parser.add_argument('--default-config-files', dest='default_cfg', action='store_true')
    parser.add_argument('--dev-image', action='store_true', help='Create a development image installer')
    parser.add_argument('--extra-funos-suffix', action='append', help='Extra funos elf suffix to use')
    parser.add_argument('--funos-type', help='FunOS build type (storage, core etc.)')
    parser.add_argument('--with-csrreplay', action='store_true', help='Include csr-replay blob')

    args = parser.parse_args()

    if args.default_cfg == False and len(args.config) == 0:
        parser.error("One of '--default-config-files' or a list of config files is required")

    funos_suffixes = [f'-{args.funos_type}' if args.funos_type else '', args.chip]
    bundle_funos_type = f'{args.funos_type}-' if args.funos_type else ''

    if args.release:
        funos_suffixes.append('release')

    if args.extra_funos_suffix:
        funos_suffixes.extend(args.extra_funos_suffix)

    args.funvisor = args.chip in CHIP_WITH_FUNVISOR

    args.sdkdir = os.path.abspath(args.sdkdir) # later processing fails if relative path is given
    funos_appname = "funos{}.stripped".format('-'.join(funos_suffixes))
    rootfs_files = ALL_ROOTFS_FILES[args.chip]

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
                'bin/flash_tools/mmc_blobs_fungible.json',
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
    board_cfg_list = 'boardcfg_profile_list.json'
    fvht_list_file = None
    default_board =  BOARD_CFG_PER_CHIP_SKU_DEFAULT.get(args.chip)
    if not default_board:
        print('Unsupported chip: {}!'.format(args.chip))
        exit(1)

    if wanted('prepare') or wanted('sdk-prepare'):
        gf.merge_configs(config, json.loads(EEPROM_CONFIG_OVERRIDE), only_if_present=True)
        gf.merge_configs(config, json.loads(HOST_FIRMWARE_CONFIG_OVERRIDE), only_if_present=True)
        gf.merge_configs(config, json.loads(FUNOS_CONFIG_OVERRIDE.format(funos_appname=funos_appname)), only_if_present=True)
        gf.merge_configs(config, json.loads(EEPROM_LIST_CONFIG_OVERRIDE.format(eeprom_list=eeprom_list)), only_if_present=True)
        gf.merge_configs(config, json.loads(CSRR_CONFIG_OVERRIDE.format(chip=args.chip)), only_if_present=True)
        gf.merge_configs(config, json.loads(BOARD_CFG_LIST_CONFIG_OVERRIDE.format(board_cfg_list=board_cfg_list)), only_if_present=True)
        gf.merge_configs(config, json.loads(BOARD_CONFIG_OVERRIDE.format(sku_name=default_board)), only_if_present=True)

        if not args.with_csrreplay:
            try:
                del config['signed_images']['csr_override.bjson.signed']
            except:
                # ignore errors, the csr_override entry might not exist depending
                # on which input configs were used
                pass

        fvht_config = {}
        fvht_list_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        for rootfs, _ in rootfs_files:
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

    config_sdk_package = config['global_config'].get('sdk_package') if config.get('global_config') else False

    chip_specific_files = () if config_sdk_package else CHIP_SPECIFIC_FILES.get(args.chip, ())

    if wanted('prepare') or wanted('sdk-prepare'):
        # paths to application binaries in SDK tree
        paths = [ "bin",
                "FunSDK/sbpfw/roms",
                "FunSDK/dpu_eepr",
                "FunSDK/nvdimm_fw",
                "feature_sets",
                "FunSDK/config/pipeline"
                ]
        sdkpaths = [os.path.join(args.sdkdir, path) for path in paths]

        paths_chip_specific = [ "FunSDK/u-boot/{chip}",
                "FunSDK/sbpfw/firmware/chip_{chip}_emu_0",
                "FunSDK/sbpfw/pufrom/chip_{chip}_emu_0",
		 "feature_sets/boardcfg/{chip}",
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
        utils.append(os.path.join('FunSDK/dpu_eepr', eeprom_list))

        for app in utils:
            shutil.copy2(os.path.join(args.sdkdir, app), os.path.basename(app))

        shutil.rmtree('install_tools', ignore_errors=True)
        shutil.copytree(os.path.join(args.sdkdir, 'bin/flash_tools/install_tools'),
            'install_tools')
        if _want_funvisor(args):
            for rootfs, _ in rootfs_files:
                root_file = os.path.join(args.sdkdir, 'deployments', rootfs)
                shutil.copy2(root_file, rootfs)
                try:
                    shutil.copy2(root_file + '.version', rootfs + '.version')
                except FileNotFoundError:
                    pass

        if wanted('prepare'):
            # these files are not needed in sdk-prepare
            shutil.copy2(funos_appname, _mfg(funos_appname))
            shutil.copy2(funos_appname, _mfgnofv(funos_appname))
            shutil.copy2(funos_appname, _nor(funos_appname))

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
            cmd = [ localdir('make_emulation_emmc.py'),
                    '-w', '.',
                    '-o', '.',
                    '--appfile', funos_appname,
                    '--filesystem',
                    '--signed',
                    '--bootscript-only']
            if args.with_csrreplay:
                cmd.extend(['--blob', 'csr_override_{chip}.bjson'.format(chip=args.chip)])

            subprocess.check_call(cmd)

        if _want_funvisor(args):
            cmd = [ localdir('gen_fgpt.py'), 'fgpt.unsigned' ]
            subprocess.call(cmd)

            cmd = [ localdir('xdata.py'),
                    '-r',
                    '--data-offset=4096',
                    '--data-alignment=512',
                    '--padding=4',
                    'fvos.unsigned',
                    'add',
                    os.path.join(args.sdkdir,
                        'bin/cc-linux-yocto/mips64hv/vmlinux.bin') ]
            subprocess.call(cmd)

            for rootfs, _ in rootfs_files:
                cmd = [ localdir('gen_hash_tree.py'),
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
        cmd = [ localdir('make_emulation_emmc.py'),
                '-w', '.',
                '-o', '.',
                '--appfile', funos_appname,
                '--filesystem',
                '--signed',
                '--bootscript-only']

        if args.with_csrreplay:
            cmd.extend(['--blob', 'csr_override_{chip}.bjson'.format(chip=args.chip)])
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

        cmd = [ localdir('make_emulation_emmc.py'),
                '-w', '.',
                '-o', '.',
                '--appfile', 'funos.signed.bin',
                '--fsfile', 'boot.img.signed',
                '--filesystem',
                '--signed' ]
        if args.with_csrreplay:
                cmd.extend(['--blob', 'csr_override.bjson.signed'])
        subprocess.check_call(cmd)

        if _want_funvisor(args):
            for rootfs, _ in rootfs_files:
                cmd = [ localdir('gen_hash_tree.py'),
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

        def skip_tarfile_entry(e):
            if e.get("no_export", False):
                return True
            if e.get("only_with_funvisor", False):
                return not _want_funvisor(args)
            return False

        with open("image.json") as f:
            images = json.load(f)
            tarfiles.extend([key for key,value in images['signed_images'].items()
                                if not skip_tarfile_entry(value)])
            tarfiles.extend([key for key,value in images['signed_meta_images'].items()
                                if not skip_tarfile_entry(value)])

        with open("mmc_image.json") as f:
            images = json.load(f)
            tarfiles.extend([key for key,value in images['generated_images'].items()
                                if not skip_tarfile_entry(value)])

        tarfiles.append('image.json')
        tarfiles.append('mmc_image.json')
        if _want_funvisor(args):
            for rootfs, _ in rootfs_files:
                tarfiles.append(_rootfs('fvht.bin', rootfs))
                tarfiles.append(rootfs)
        tarfiles.extend(glob.glob('qspi_image_hw.bin.*'))

        for chip_file in chip_specific_files:
            tarfiles.append(os.path.basename(chip_file))

        if os.path.exists('.version'):
            tarfiles.append('.version')

        with tarfile.open(f'{bundle_funos_type}{args.chip}_sdk_signed_release.tgz', mode='w:gz') as tar:
            for f in tarfiles:
                tar.add(f)

        os.chdir(curdir)

    if wanted('bundle'):
        def skip_bundle_entry(e):
            if e.get("no_export", False):
                return True
            if e.get("no_bundle", False):
                return True
            if e.get("only_with_funvisor", False):
                return not _want_funvisor(args)
            return False

        def bundle_gen(rootfs, bundle_target, suffix):
            os.chdir(args.destdir)
            shutil.rmtree('bundle_installer', ignore_errors=True)
            os.mkdir('bundle_installer')
            bundle_images = []

            with open("image.json") as f:
                images = json.load(f)
                bundle_images.extend([key for key,value in images.get('signed_images',{}).items()
                                    if not skip_bundle_entry(value)])
                bundle_images.extend([key for key,value in images.get('signed_meta_images', {}).items()
                                    if not skip_bundle_entry(value)])

            with open("mmc_image.json") as f:
                images = json.load(f)
                bundle_images.extend([key for key,value in images.get('generated_images',{}).items()
                                    if not skip_bundle_entry(value)])

            bundle_images.extend([
                'install_tools/run_fwupgrade.py',
                'install_tools/setup.sh',
                'image.json'
            ])

            if _want_funvisor(args):
                bundle_images.extend([
                    _rootfs('fvht.bin', rootfs),
                    rootfs
                ])

                if os.path.exists(rootfs + '.version'):
                    bundle_images.append(rootfs + '.version')

            for chip_file in chip_specific_files:
                bundle_images.append(os.path.basename(chip_file))

            if os.path.exists('.version'):
                bundle_images.append('.version')

            for f in bundle_images:
                os.symlink(os.path.join(os.path.abspath(os.curdir), f), os.path.join('bundle_installer', os.path.basename(f)))

            with open(os.path.join('bundle_installer', '.setup'), "w") as cfg:
                cfg.writelines([
                    'ROOTFS_NAME="{}"\n'.format(rootfs),
                    'CHIP_NAME="{}"\n'.format(args.chip.upper()),
                    'DEV_IMAGE={}\n'.format(1 if args.dev_image else 0),
                    'SDK_BUNDLE={}\n'.format(1 if config_sdk_package else 0),
                    'WITH_FUNVISOR={}\n'.format(1 if args.funvisor else 0)
                ])

            bundle_name = 'development_image' if args.dev_image else bundle_target
            makeself = [
                os_utils.path_fixup('makeself'),
                '--follow',
                'bundle_installer',
                f'setup_bundle_{bundle_funos_type}{bundle_name}{suffix}.sh',
                f'{"CCLinux/" if args.funvisor else ""}FunOS {args.funos_type} {bundle_name} installer',
                './setup.sh'
            ]

            subprocess.call(makeself)
            os.chdir(curdir)

        fv = args.funvisor
        for rootfs, bundle_target in rootfs_files:
            # List of tuples (use_funvisor, suffix) to generate bundles
            # For DPUs with funvisor support add an extra '_nofv' suffix to bundles
            # and preserve default name for funvisor bundles.
            fv_opts = [(False, '_nofv'), (True, '')] if args.chip in CHIP_WITH_FUNVISOR \
                    else [(False, '')]
            for fv_opt, suffix in fv_opts:
                args.funvisor = fv_opt
                bundle_gen(rootfs, bundle_target, suffix)
        args.funvisor = fv


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

        rootfs, _ = rootfs_files[0]
        mfgxdata = {
            # fourc : (target, filename)
            'husc' : ('nor', 'hu_sbm_serdes.bin'),
            'hbsb' : ('nor', 'hbm_sbus.bin'),
            'kbag' : ('nor', 'key_bag.bin'),
            'host' : ('nor', 'host_firmware_packed.bin'),
            'sbpf' : ('nor', 'esecure_firmware_all.bin'),
            'emmc' : ('mmc', 'emmc_image.bin'),
        }

        mfgxdata_fv = {
            # fourc : (target, filename)
            'fgpt' : ('mmc', 'fgpt.signed'),
            'fvp1' : ('mmc', 'fvos.signed'),
            'fvp2' : ('mmc', rootfs),
            'fvp4' : ('mmc', _rootfs('fvht.bin', rootfs)),
        }

        # that's a bit hacky ... need something better here
        if args.chip == 'f1' or args.chip == 'f1d1':
            mfgxdata_fv['ccfg'] = ('mmc', 'ccfg-no-come.signed.bin')
            mfgxdata['ccfg'] = ('mmc', 'ccfg-legacy.signed.bin')
        elif args.chip == 's1':
            mfgxdata['ccfg'] = ('mmc', 'ccfg-s1-demo-10g_mpg.signed.bin')


        mfgxdata_without_fv = mfgxdata
        mfgxdata_with_fv = mfgxdata.copy()
        mfgxdata_with_fv.update(mfgxdata_fv)

        mfgxdata_lists = {
            'fw_upgrade_all': 'all',
            'fw_upgrade_nor': 'nor',
            'fw_upgrade_mmc': 'mmc'
        }

        def _gen_xdata_funos(outname_modifier, target=None, with_fv=True):
            mfgxdata = mfgxdata_with_fv if with_fv else mfgxdata_without_fv
            outname_suffix = outname_modifier.__name__
            print("Generating MFG image type {}".format(outname_suffix))
            for fname, listtarget in mfgxdata_lists.items():
                # generate upgrade lists to be embedded in xdata
                with open(fname, 'w') as f:
                    for key, (imgtarget, imgfile) in mfgxdata.items():
                        if listtarget == imgtarget or listtarget == 'all':
                            f.write("{}\n".format(key))

            with open('fw_upgrade_xdata_{}'.format(outname_suffix), 'w') as f:
                # generate complete xdata list
                for key, (imgtarget, imgfile) in mfgxdata.items():
                    if not target or imgtarget == target:
                        f.write("{} {}\n".format(key, os.path.join(os.getcwd(), imgfile)))

                for fname in mfgxdata_lists:
                    f.write("{} {}\n".format(fname, os.path.join(os.getcwd(), fname)))

            cmd = [ localdir('xdata.py'),
                    outname_modifier(funos_appname),
                    'add-file-lists',
                    'fw_upgrade_xdata_{}'.format(outname_suffix) ]
            subprocess.call(cmd)

            # stash xdata lists for debugging
            stash_dir = 'xdata_{}'.format(outname_suffix)
            shutil.rmtree(stash_dir, ignore_errors=True)
            os.mkdir(stash_dir)
            for fname in mfgxdata_lists:
                shutil.move(fname, stash_dir)

            # take a copy of all funos default settings for signing
            # and only override filenames used
            mfg_app_config = config['signed_images'].get('funos.signed.bin').copy()
            mfg_app_config['source'] = outname_modifier(funos_appname)
            config['signed_mfg_images'] = {
                outname_modifier(funos_appname, signed=True) : mfg_app_config
            }
            gf.set_search_paths([os.getcwd()])
            gf.create_file(outname_modifier(funos_appname, signed=True), section='signed_mfg_images')


        if args.chip in CHIP_WITH_FUNVISOR:
            _gen_xdata_funos(_mfg, with_fv=True)
        _gen_xdata_funos(_mfgnofv, with_fv=False)
        _gen_xdata_funos(_nor, 'nor')

        os.chdir(curdir)

    if wanted('mfgtarball'):
        os.chdir(args.destdir)
        tarfiles = []

        mod = _mfg if args.chip in CHIP_WITH_FUNVISOR else _mfgnofv
        tarfiles.extend(glob.glob('qspi_image_hw.bin.*'))
        tarfiles.append(mod(funos_appname, signed=True))

        if os.path.exists('.version'):
            tarfiles.append('.version')

        with tarfile.open(f'{bundle_funos_type}{args.chip}_mfg_package.tgz', mode='w:gz') as tar:
            for f in tarfiles:
                tar.add(f)

        os.chdir(curdir)


if __name__=="__main__":
    main()
