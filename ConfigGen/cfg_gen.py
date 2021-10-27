#!/usr/bin/env python2.7

# cfg_gen.py
# The config generator is intended to simplify configuration file maintenance,
# now that we are getting more files. The files are all stored in a flat
# layout (configs/*.cfg) and are combined into one default.cfg. This is
# subject to change as requirements for different configurations grow.
#
# Created by Michael Boksanyi, August 10 2017
# Modified by Fred stanley, Nov 9 2017
# Copyright Fungible Inc. 2017

import os, sys
import glob, datetime
import argparse, tempfile
import json
import logging
from itertools import chain
from string import Template
from pprint import pprint
import fnmatch

import jsonutils
from hu_cfg_gen import HUCfgGen
from sku_cfg_gen import SKUCfgGen
from hwcap_cfg_gen import HWCAPCodeGen
from nu_cfg_gen import NUCfgGen
from storage_cfg_gen import StorageCfgGen

logger = logging.getLogger("cfg_gen")
logging.basicConfig(level=logging.INFO)

# Creates nu config
def _generate_nu_config(config_root_dir, output_dir, target_chip, target_machine):
    logger.info('Processing nu config')

    nu_cfg_gen = NUCfgGen(config_root_dir, output_dir,
                          target_chip, target_machine)
    nu_cfg = nu_cfg_gen.generate_config()

    return nu_cfg

# Creates hu config
def _generate_hu_config(config_root_dir, output_dir):
    logger.info('Processing hu config')

    hu_cfg_gen = HUCfgGen(config_root_dir, output_dir)
    hu_cfg = hu_cfg_gen.generate_config()

    return hu_cfg

# Creates nu csr replay config
def _generate_nu_csr_replay_config(config_root_dir, output_dir, target_chip, target_machine):
    logger.info('Processing nu csr replay config')

    nu_cfg_gen = NUCfgGen(config_root_dir, output_dir,
                          target_chip, target_machine)
    nu_csr_replay_cfg = nu_cfg_gen.csr_replay_config_generate()

    return nu_csr_replay_cfg

# Creates nu config
def _generate_sku_config(config_root_dir, sdk_dir, output_dir, target_chip, target_machine):
    logger.info('Processing per sku config:')

    sku_cfg_gen = SKUCfgGen(config_root_dir, sdk_dir, output_dir, target_chip, target_machine)

    return sku_cfg_gen._get_sku_config()

# Creates stats config
def _generate_stats_config(config_root_dir):
    logger.info('Processing stats config')
    stats_cfg = dict()

    for cfg in glob.glob(os.path.join(config_root_dir, 'generated/*.cfg')):
        logger.debug('Processing {}'.format(cfg))
        with open(cfg, 'r') as f:
            cfg_json = f.read()
            cfg_json = jsonutils.standardize_json(cfg_json)
            cfg_json = json.loads(cfg_json)
            stats_cfg = jsonutils.merge_dicts(stats_cfg, cfg_json)
    return stats_cfg

# creates module specific configs. from the config root dir, modules can
# specify their own configurations by putting it in the path:
#
#   modules/<module_name>/x/y/z.cfg
#
# the directory names are used as the path to the dictionary, the actual
# configuration file name is not used.
#
# for example, the following two files:
#
#   benturrubiates at vodex :: cat modules/tcp/tcp.cfg
#   {
#           max_rxmt_count: 3,
#   }
#   benturrubiates at vodex :: cat modules/tcp/x/tcp.cfg
#   {
#           y: 3,
#   }
#
# will eventually generate:
#
#   "modules":{
#      "tcp":{
#         "x":{
#            "y":3
#         },
#         "max_rxmt_count":3
#      }
#   }
#
# in the final config.
def _generate_modules_config(config_root_dir):
    # Python 2.7 glob does not support a recursive glob. We want to allow
    # nesting within the modules path. So, search using os.walk.
    def _find_modules_configs():
        matches = []
        for root, dirs, files in os.walk(config_root_dir):
            for match in fnmatch.filter(files, '*.cfg'):
                matches.append(os.path.join(root, match))

        return matches

    logger.info('Processing modules config')
    out_cfg = dict()

    for cfg in _find_modules_configs():
        logger.info('Processing {}'.format(cfg))

        with open(cfg, 'r') as f:
            cfg_json = f.read()
            cfg_json = jsonutils.standardize_json(cfg_json)
            cfg_json = json.loads(cfg_json)

        # Gets the path relative to the config root, e.g.
        #   'tcp/tcp.cfg'
        cfg_path = os.path.relpath(cfg, config_root_dir)

        # Gets the parent paths as a list, e.g.
        #   ['tcp']
        parents = cfg_path.split(os.path.sep)[:-1]

        # Builds the heirarchy outwards from the inside, returns something
        # like:
        #   {'modules': {'tcp': {cfg_json}}}
        for parent in reversed(parents):
            cfg_json = {parent: cfg_json}
        cfg_json = {"modules": cfg_json}

        # Merge recursively. Merges subpaths so hierarchies are possible.
        out_cfg = jsonutils.merge_dicts_recursive(out_cfg, cfg_json)

    # Return a single config for everything under config_root_dir/modules
    return out_cfg

# Creates storage config
def _generate_storage_config(config_root_dir, output_dir,
                             target_chip, target_machine):
    logger.info('Processing storage config')

    storage_cfg_gen = StorageCfgGen(config_root_dir, output_dir,
                                    target_chip, target_machine)
    storage_cfg = storage_cfg_gen.generate_config()

    return storage_cfg

# filename -> arbitrary json
def _read_json_file(fname):
    try:
        sjs=None
        fl = open(fname)
        fls = fl.read()
        sjs = jsonutils.standardize_json(fls)
        js = json.loads(sjs)
    except:
        print("Exception occurred reading/parsing json file %s" % fname)
        print(sjs)
        raise

    return js

# filename -> dict, or die trying
def _read_json_file_as_dict(fname):
    js = _read_json_file(fname)
    try:
        assert(isinstance(js, dict))
    except:
        print("JSON file %s is not a dict" % fname)
        raise

    return js

# TODO: add more validations as necessary
def _validate_profile_cfg(fname, js):
    assert(isinstance(js, dict))
    if ("subprofiles" not in js):
        raise RuntimeError("subprofile %s is missing subprofiles key" % fname)
    assert(isinstance(js["subprofiles"], dict))


# TODO: add more validations as necessary
def _validate_subprofile_cfg(fname, js):

    assert(isinstance(js, dict))
    if ("key_path" not in js):
        raise RuntimeError("subprofile %s is missing key_path" % fname)
    print(js)
    print(js["key_path"])
    print(type(js["key_path"]))

    assert(isinstance(js["key_path"], basestring))

    if ("weight" in js):
        assert(isinstance(js["weight"], int))
    if ("replace" in js):
        assert(isinstance(js["replace"], bool))

# load all the .cfg options for a subprofile from a directory.  called
# for global, chip and board paths. "global_path" is True if we expect
# to skip the "subprofile-xyz.cfg" file when we encounter it. If this
# is not the global_path, that file should not exist.
def _load_subprofile_fragments(subdir, global_path):

    fragments = {}

    cfgglob = os.path.join(subdir, "*.cfg")
    for fname in glob.glob(cfgglob):

        # base filename and subprofile fragment name used, eg:
        # foo_profile = fragment
        bname = os.path.basename(fname)
        pname = os.path.splitext(bname)[0]

        # remove "-foo" suffix
        if ("-" in pname):
            pname = pname.split("-")[0]
        assert(len(pname) > 0) # "-foo.cfg" is nonsense

        # see if this is a subprofile descriptor
        if (fnmatch.fnmatch(bname, "subprofile-*.cfg")):
            if (not global_path):
                raise RuntimeError("Found subprofile descriptor found outside subprofile global path: %s" % fname)

            # otherwise, ignore it
            continue

        # read the json file -- any json is valid
        js = _read_json_file(fname)

        # append it to the list
        if (pname in fragments):
            raise RuntimeError("Error: duplicate json fragment: %s (%s)" % (pname, fname))
        fragments[pname] = js

    return fragments

def _load_subprofiles_and_fragments(spglob, subprofiles, stype, sval):

    sglob = os.path.join(spglob, "*_profile")
    for subprof in glob.glob(sglob):
        if (not os.path.isdir(subprof)):
            print("WARNING: %s is not a directory, ignoring" % subprof)
            continue

        # get the name
        subname = os.path.basename(subprof)

        # make sure it's valid
        assert(subname in subprofiles)

        sub_fragments = _load_subprofile_fragments(subprof, False)
        subprofiles[subname][stype][sval] = sub_fragments

# boot-time configuration profiles. see profiles_config/HOWTO.md
def _generate_profiles_config(config_root_dir, target_chip, target_boards):

    ## root of the profile configs
    pdir = os.path.join(config_root_dir, "profiles_config")

    ## read the subprofile descriptions

    # subprofiles are described in  "subprofiles/foo_subprofile" directories
    subprofiles = {}
    sglob = os.path.join(pdir, "subprofiles", "*_profile")
    for subdir in glob.glob(sglob):
        if (not os.path.isdir(subdir)):
            print("WARNING: %s is not a directory, ignoring" % subdir)
            continue

        # get the name
        subname = os.path.basename(subdir)

        # the definition of a subprofile is in
        # "subprofile-whatever.cfg" in the "foo_subprofile" directory.
        # the "whatever" is ignored, just there to disambiguate many
        # files otherwise named "subprofile.cfg".
        cfgglob = os.path.join(subdir, "subprofile-*.cfg")
        cfgs = glob.glob(cfgglob)

        if (len(cfgs) == 0):
            # no descriptor fail
            raise RuntimeError("error: subprofile %s is missing a subprofile-XYZ.cfg descriptor" % subdir)

        if (len(cfgs) > 1):
            # multi descriptor fail
            raise RuntimeError("error: subprofile %s has multiple descriptor files: %s" %s (subdir, cfgs))

        descfilename = cfgs[0]
        print("subprofile %s using descriptor %s" % (subdir, descfilename))

        # parse it
        js = _read_json_file_as_dict(descfilename)

        # make sure it meets static minimum requirements. other
        # validations come later
        _validate_subprofile_cfg(descfilename, js)

        # setup the skeleton dict with the descriptor
        subprofiles[subname] = {"descriptor": js,
                                "global":{},
                                "chip":{},
                                "board":{}}

        # load all the global fragments, if any, and append to the descriptor
        sub_fragments = _load_subprofile_fragments(subdir, True)
        subprofiles[subname]["global"] = sub_fragments

    # read all the fragments for the chip
    chipdir = os.path.join(pdir, "chip", target_chip)
    _load_subprofiles_and_fragments(chipdir, subprofiles, "chip", target_chip)

    # read all the fragments for all the boards
    bglob = os.path.join(pdir, "board", "*")
    for boarddir in glob.glob(bglob):
        if (not os.path.isdir(boarddir)):
            print("WARNING: %s is not a directory, ignoring" % boarddir)
            continue

        # get the name
        boardname = os.path.basename(boarddir)

        # FIXME: only include the ones we know we need
        # if (boardname not in target_boards):
        #      continue

        _load_subprofiles_and_fragments(boarddir, subprofiles,
                                        "board", boardname)

    # parse the list of profiles
    profiles = {}
    pglob = os.path.join(pdir, "profiles", "*.cfg")
    for cfg in glob.glob(pglob):
        # extract the name
        bname = os.path.basename(cfg)
        pname = os.path.splitext(bname)[0]

        # read it
        js = _read_json_file_as_dict(cfg)

        # make sure all the subprofiles exist
        subs = js.get("subprofiles")
        if (subs is None):
            raise RuntimeError("profiles %s missing required subprofiles" % pname)

        # validate all the keys & values that we can do statically
        print("found profile %s" % pname)
        _validate_profile_cfg(pname, js)

        # add it to the list
        profiles[pname] = js


    # make the big dict and return that
    profiles_config = {"profiles_config":
                       {
                           "profiles": profiles,
                           "subprofiles": subprofiles,
                       }
    }

    return profiles_config

def _load_workerpool_config(wpconfig):

    # read the input file
    fl = open(wpconfig)
    js = json.load(fl)

    # bury it into the appropriate place in the tree
    wp_cfg = {}

    # modules/nucleus/workerpools/policies in nucleus 
    wp_cfg = {"modules": {"nucleus": {"workerpools": {"policies": js}}}}

    return wp_cfg


def build_target_is_posix(target_machine):
    if 'posix' in target_machine:
        return True
    return False

def build_target_is_emulation(target_machine):
    if 'emu' in target_machine:
        return True
    return False

def build_target_is_qemu(target_machine):
    if 'qemu' in target_machine:
        return True
    return False

# Generate funos config
def _generate_funos_default_config(config_root_dir, sdk_dir, output_dir,
                                   target_chip, target_machine, wpconfig):
    logger.info('Generating funos default config')
    funos_default_config = dict()

    nu_cfg = _generate_nu_config(config_root_dir, output_dir, target_chip, target_machine)
    funos_default_config = jsonutils.merge_dicts(funos_default_config, nu_cfg)

    hu_cfg = _generate_hu_config(config_root_dir, output_dir)
    funos_default_config = jsonutils.merge_dicts(funos_default_config, hu_cfg)

    storage_cfg = _generate_storage_config(config_root_dir, output_dir,
                                           target_chip, target_machine)
    funos_default_config = jsonutils.merge_dicts(funos_default_config, storage_cfg)

    sku_cfg = _generate_sku_config(config_root_dir, sdk_dir, output_dir, target_chip, target_machine)
    funos_default_config = jsonutils.merge_dicts(funos_default_config, sku_cfg)

    stats_cfg = _generate_stats_config(config_root_dir)
    funos_default_config = jsonutils.merge_dicts(funos_default_config, stats_cfg)

    ## process module config -- global and per-chip
    config_module_dir = os.path.join(config_root_dir,
                                     "modules_config", "modules")
    modules_cfg = _generate_modules_config(config_module_dir)

    config_chip_dir = os.path.join(config_root_dir,
                                   "modules_config", "chip", target_chip)
    if os.path.exists(config_chip_dir):
        chip_modules_cfg = _generate_modules_config(config_chip_dir)
        modules_cfg = jsonutils.merge_dicts_recursive(modules_cfg,
                                                      chip_modules_cfg)

    ## assemble into main config
    funos_default_config = jsonutils.merge_dicts(funos_default_config,
                                                 modules_cfg)
       
    ## process module config -- per-sku
    for sku in list(funos_default_config[SKUCfgGen.get_sku_path()].keys()):
        config_sku_dir = os.path.join(config_root_dir,
                                   "modules_config", "board", sku)
        if os.path.exists(config_sku_dir):
            module_cfg = _generate_modules_config(config_sku_dir)
            sku_modules_cfg = SKUCfgGen.create_sku_cfg_entry(sku, module_cfg)
            funos_default_config = jsonutils.merge_dicts_recursive(funos_default_config,
                                                    sku_modules_cfg)

    ## process profile configs

    ## FIXME: generate the list of valid boards from the existing
    ## config and pass them through
    target_boards = []
    profiles_cfg = _generate_profiles_config(config_root_dir,
                                             target_chip, target_boards)

    ## assemble into main config
    funos_default_config = jsonutils.merge_dicts(funos_default_config,
                                                 profiles_cfg)

    ## process workerpool config, if requested
    if (wpconfig is not None):
        wp_cfg = _load_workerpool_config(wpconfig)

        ## assemble into main config
        funos_default_config = jsonutils.merge_dicts_recursive(
                                                     funos_default_config,
                                                     wp_cfg)

    # write the output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    default_cfg_file = os.path.join(output_dir, "default.cfg")
    logger.info('Creating funos default config file: {}'.format(default_cfg_file))
    _f = open(default_cfg_file, 'w')

    header = '// AUTOGENERATED FILE - DO NOT EDIT\n'
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    header = header + "// Generated by " + os.path.basename(__file__) + " on " + date + " \n"
    _f.write(header)

    # indent=4 does pretty printing for us
    json.dump(funos_default_config, _f, indent=4, sort_keys=True)

    _f.close()

#Generates sku config source code
def _generate_sku_config_code(config_root_dir, sdk_dir, output_dir,
                              target_chip, target_machine):
    logger.info('Generating sku config c code')

    sku_cfg_gen = SKUCfgGen(config_root_dir, sdk_dir, output_dir,
                            target_chip, target_machine)
    sku_cfg_gen.generate_code()
    include_files = sku_cfg_gen.get_header_file_list()

    hwcap_cfg_gen = HWCAPCodeGen(config_root_dir, output_dir,
                                 target_chip, target_machine)

    hwcap_cfg_gen.generate_code(include_files)

#Generates sku eeprom files for the fungible boards and emulation build with sbp
def _generate_sku_eeprom_files(config_root_dir,
                               sdk_dir,
                               output_dir,
                               target_chip,
                               target_machine):
    logger.info('Generating eeprom files')
    sku_cfg_gen = SKUCfgGen(config_root_dir, sdk_dir, output_dir,
                            target_chip, target_machine)
    sku_cfg_gen.generate_eeprom()
    sku_cfg_gen.generate_chip_eeprom_lists()

#Generates hu config source code
def _generate_hu_config_code(config_root_dir, output_dir):
    logger.info("Generating HU config C code ")

    hucgen = HUCfgGen(config_root_dir, output_dir)
    hucgen.generate_code()

def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError('Directory: {} is not a valid path!'.format(path))

def main():
    arg_parser = argparse.ArgumentParser(
        description="Config file processing and auto generate code for funos"
        " default config, hu config, hwcap, sku id's and eeprom sku-id files")

    arg_parser.add_argument("--print-build-deps", action='store_true',
                            help="Print build dependencies")

    # Check print-build-deps arg initially, so that it can be used
    # without the other mandatory arguments added later on
    args, _ = arg_parser.parse_known_args()
    if args.print_build_deps:
        print(' '.join(SKUCfgGen.get_build_deplist() + HWCAPCodeGen.get_build_deplist()))
        return 0

    arg_parser.add_argument("--in-dir", required=True, nargs=1,
                            type=dir_path, help="input config source directory path")

    arg_parser.add_argument("--sdk-dir", type=dir_path, help="sdk directory path")

    arg_parser.add_argument("--out-dir", required=True, nargs=1, type=dir_path, help="output dir path")

    arg_parser.add_argument("--machine", required=True, nargs=1, type=str,
                            help="Target machine type")

    arg_parser.add_argument("--chip", required=True, nargs=1, type=str,
                            help="Target chip type")

    arg_parser.add_argument("--wpcfg", action='store', default=None,
                            help="Workerpool configuration file for funoscfg")

    parser = arg_parser.add_mutually_exclusive_group(required=True)

    parser.add_argument("--funoscfg", action='store_true',
                        help="Merge all the json config files and generate funos config file")

    parser.add_argument("--skucfg", action='store_true',
                        help="Generate sku id's & hwcap config c code from board & hwcap sku json config files")

    parser.add_argument("--hucfg", action='store_true',
                        help="Generate hu config c code from hu json config files")

    parser.add_argument("--nucsr-replaycfg", action='store_true',
                        help="Generates merged nu csr replay config json")

    parser.add_argument("--eeprom", action='store_true',
                        help=("Generate eeprom sku id files from board config"
                              " json files & hwcap json config files"))

    # Now parse all args once again
    args = arg_parser.parse_args()
    logger.debug('Command line args: {}'.format(args))

    if args.funoscfg:
        _generate_funos_default_config(args.in_dir[0],
                                       args.sdk_dir, args.out_dir[0],
                                       args.chip[0], args.machine[0],
                                       args.wpcfg)
        _generate_sku_config_code(args.in_dir[0], args.sdk_dir, args.out_dir[0],
                                  args.chip[0], args.machine[0])
        _generate_hu_config_code(args.in_dir[0], args.out_dir[0])

    if args.hucfg:
        _generate_hu_config_code(args.in_dir[0], args.out_dir[0])

    if args.skucfg:
        _generate_sku_config_code(args.in_dir[0], args.sdk_dir, args.out_dir[0],
                                  args.chip[0], args.machine[0])

    if args.nucsr_replaycfg:
        _generate_nu_csr_replay_config(args.in_dir[0], args.out_dir[0],
                                       args.chip[0], args.machine[0])

    if args.eeprom:
        _generate_sku_eeprom_files(args.in_dir[0], args.sdk_dir, args.out_dir[0],
                                   args.chip[0], args.machine[0])

if __name__ == "__main__":
    main()
