#!/usr/bin/env python2.7

#This module generates merged config of all skus, sku-id definitions and eeprom files.

import os, sys, logging, glob
from jinja2 import Template
from jinja2 import Environment
from jinja2 import FileSystemLoader
import datetime
import subprocess
import struct
import tempfile
import json
import jsonutils
from itertools import chain
import argparse
from hwcap_cfg_gen import HWCAPCodeGen
import copy
from default_cfg_gen import DefaultCfgGen
from sku_board_layer_cfg_gen import BoardLayer

logger = logging.getLogger('sku_cfg_gen')
logger.setLevel(logging.INFO)


# For each EEPR file, emit multiple variants based
# on "struct puf_rom_eeprom_image_s" flags
EEPROM_IMAGE_FLAGS_S1_1_1GHZ_CHICKEN = 1
CHIP_FLAG_EEPR_VARIANTS = {
    "s1": [("", 0), ("_1_1G", EEPROM_IMAGE_FLAGS_S1_1_1GHZ_CHICKEN)]
}

class SKUCfgGen():
    sku_h_tmpl = 'platform_sku_h.j2'
    sku_c_tmpl = 'platform_sku_c.j2'
    sku_file_prefix = 'platform_sku'

    def __init__(self, input_dir, sdk_dir, output_dir, target_chip, target_machine):
        self.input_dir = input_dir
        self.sdk_dir = sdk_dir
        self.output_dir = output_dir
        self.target_chip = target_chip
        self.target_machine = target_machine

    def _get_fungible_board_id_config(self):
        board_id_cfg = dict()
        file_name = os.path.join(self.input_dir, 'sku_config/fungible_boards.cfg')
        logger.debug('Processing fungible boards file: {}'.format(file_name))
        board_id_cfg = jsonutils.load_fungible_json(file_name)

        return board_id_cfg.get('fungible_boards', None)

    def get_posix_or_emu_configs(self, board_cfg):
        """Get the configuration for all the posix or emulations that
        use the target chip.
        """
        def_cfg = dict()
        default_cfg_gen = DefaultCfgGen(self.input_dir, self.target_chip)

        # Get the default configuration
        def_cfg = default_cfg_gen.get_defaults()

        _path = 'sku_config/'

        if 'posix' in (self.target_machine):
            _path = _path + 'posix/%s_*.cfg' % self.target_chip
        else:
            _path = _path + 'emulation/%s_*.cfg' % self.target_chip

        file_patterns = [_path]
        logger.debug('board config paths: {}'.format(file_patterns))
        for file_pat in file_patterns:
            for cfg in glob.glob(os.path.join(self.input_dir, file_pat)):
                logger.debug('Processing posix or emu per sku config: {}'.format(cfg))

                try:
                    sku_json = jsonutils.load_fungible_json(cfg)
                except:
                    logger.error("Failed to load config file: {}".format(cfg))
                    raise

                default_cfg_gen.apply_defaults(sku_json, def_cfg)
                board_cfg = jsonutils.merge_dicts(board_cfg, copy.deepcopy(sku_json))

        return board_cfg

    def is_cfg_target_board(self, sku_json):
        """Check if the configuration file is for the target
        being built.
        """
        for key in list(sku_json['skus'].keys()):
            # First check the target chip
            if 'chip' not in sku_json['skus'].get(key, {}).get('PlatformInfo', {}):
                continue
            chip = sku_json['skus'][key]['PlatformInfo']['chip']
            if chip != self.target_chip:
                return False
            # Next check the configuration file is for a board
            if 'machine' not in sku_json['skus'].get(key, {}).get('PlatformInfo', {}):
                return False
            machine = sku_json['skus'][key]['PlatformInfo']['machine']
            if machine != 'board':
                return False
            return True

        return False

    def get_board_config_parent(self, sku_json):
        return sku_json['skus'].values()[0].get('PlatformInfo', {}).get('inherit')

    def get_board_configs(self, board_cfg):
        """Get the configuration for all the boards that use the target
        chip.
        """
        def_cfg = dict()
        default_cfg_gen = DefaultCfgGen(self.input_dir, self.target_chip)

        # Get the default configuration
        def_cfg = default_cfg_gen.get_defaults()

        _path = 'sku_config/*/*.cfg'
        file_patterns = [_path]
        remaining_board_configs = list()
        raw_board_configs = dict()
        for file_pat in file_patterns:
            for cfg in glob.glob(os.path.join(self.input_dir, file_pat)):
                # Skip board layer files and defaults files
                if 'sku_config/defaults' in cfg:
                    continue
                logger.debug('Processing board per sku config: {}'.format(cfg))

                try:
                    sku_json = jsonutils.load_fungible_json(cfg)
                except:
                    logger.error("Failed to load config file: {}".format(cfg))
                    raise

                if len(sku_json['skus']) > 1:
                    logger.error("Only single sku per file supported")
                    raise

                # stash this board config for processing inherited configs
                raw_board_configs[sku_json['skus'].keys()[0]] = copy.deepcopy(sku_json)

                if self.get_board_config_parent(sku_json):
                    # add this config to the list for processing later, as the parent
                    # configuration might not be available at this time
                    remaining_board_configs.append(sku_json)
                    continue

                # skip processing if the board is not for a given target
                # this is not done earlier to allow inherited boards to override
                # target choice, so a board for a 'wrong' target may still be added
                # to 'raw_board_configs'
                if not self.is_cfg_target_board(sku_json):
                    continue

                # Apply defaults to the SKU file
                default_cfg_gen.apply_defaults(sku_json, def_cfg)

                # Apply the board layer configuration to the SKU file
                board_layer = BoardLayer(self.input_dir, self.target_chip)
                board_layer.apply_board_layer(sku_json, def_cfg)

                board_cfg = jsonutils.merge_dicts(board_cfg, copy.deepcopy(sku_json))

        for sku_json in remaining_board_configs:
            sku = sku_json['skus'].keys()[0]
            parent = self.get_board_config_parent(sku_json)

            # check if the board is for a given target - if this is a 'base' board that was
            # used for inheriting a config, then it may be targeting a different dpu
            if not self.is_cfg_target_board(sku_json):
                continue

            # Create new sku based on the parent sku but retain original PlatformInfo
            sku_json['skus'][sku] = jsonutils.merge_dicts_recursive(
                dict(filter(lambda e: e[0] != 'PlatformInfo', raw_board_configs[parent]['skus'][parent].items())),
                sku_json['skus'][sku])

            # Apply defaults to the SKU file
            default_cfg_gen.apply_defaults(sku_json, def_cfg)

            # Apply the board layer configuration to the SKU file
            board_layer = BoardLayer(self.input_dir, self.target_chip)
            board_layer.apply_board_layer(sku_json, def_cfg)

            board_cfg = jsonutils.merge_dicts(board_cfg, copy.deepcopy(sku_json))

        return board_cfg

    def get_additions(self, board_cfg, addition_machine):
        """Add addtional configuration if needed."""
        _path = 'sku_config/additions/%s/*.cfg' % self.target_chip
        file_patterns = [_path]
        logger.debug('Additional config paths: {}'.format(file_patterns))
        for file_pat in file_patterns:
            for cfg in glob.glob(os.path.join(self.input_dir, file_pat)):
                logger.debug('Processing additions for per sku config: {}'.format(cfg))
                try:
                    sku_json = jsonutils.load_fungible_json(cfg)
                except:
                    logger.error("Failed to load config file: {}".format(cfg))
                    raise

                # Check the additional file is for the machine being built
                if 'machine' not in sku_json['PlatformInfo'].keys():
                    continue
                machine = sku_json['PlatformInfo']['machine']
                if machine != addition_machine:
                    continue;

                board_cfg = jsonutils.merge_dicts(board_cfg, sku_json)

        return board_cfg

    def _get_sku_config(self):
        board_cfg = dict()

        if 'posix' in (self.target_machine):
            board_cfg = self.get_posix_or_emu_configs(board_cfg)
            addition_machine = 'posix'
        elif 'emu' in (self.target_machine):
            board_cfg = self.get_posix_or_emu_configs(board_cfg)
            addition_machine = 'emulation'
        else:
            board_cfg = self.get_board_configs(board_cfg)
            addition_machine = 'board'

        # Process additional configuration files
        board_cfg = self.get_additions(board_cfg, addition_machine)

        return board_cfg

    def get_fungible_board_sku_ids(self, all_target_chips=False):
        sku_id_list = dict()
        fun_board_cfg = self._get_fungible_board_id_config()
        for board in fun_board_cfg:
            board_name = board.get('name', None)
            if not board_name:
                raise argparse.ArgumentTypeError('sku name is empty!')
            asic_count =  board.get('asic_count', 0)
            if not asic_count:
                 raise ValueError('Invalid asic count for {}!'.format(board_name))
            board_id_offset = board.get('board_id_offset', -1)
            if not (board_id_offset >= 0):
                raise ValueError('Invalid board id offset:{} for {}!'.format(
                    board_id_offset, board_name))
            chip_type =  board.get('asic', None)
            if ((all_target_chips == False) and (chip_type != self.target_chip)):
                continue
            sku_name = board_name
            for asic in range(asic_count):
                if asic_count > 1:
                    sku_name = board_name + '_{}'.format(asic)
                sku_id = (0x1 << 16) + (board_id_offset << 8) + asic
                sku_id_list[sku_name] =  sku_id

        return sku_id_list

    def get_chip_for_sku_id(self, sku_id):
        # get the full list
        fun_board_cfg = self._get_fungible_board_id_config()
        for board in fun_board_cfg:
            board_name = board.get('name', None)
            if (board_name != sku_id):
                continue

            # we found the board, return the chip name
            return board.get("asic")
        
        # board not found?
        return None

    def _get_board_id_from_offset(self, board_id_offset):
        return (0x1 << 8) + board_id_offset

    def _get_board_sku_id_from_offset(self, offset, asic_inst):
        if not (offset > 0x0 and ((0x1 << 24) - 1)):
            raise ValueError(
                'Invalid board id offset:{} for {}!'.format(
                    offset, board_name))
        if asic_inst < 0 or asic_inst > 255:
            raise ValueError(
                'Invalid asic_inst :{}!'.format(asic_inst))
        return (self._get_board_id_from_offset(offset) << 8) + asic_inst

    def get_fungible_board_ids(self):
        board_id_list = dict()
        fun_board_cfg = self._get_fungible_board_id_config()
        for board in fun_board_cfg:
            board_name = board.get('name', None)
            if not board_name:
                raise argparse.ArgumentTypeError('sku name is empty!')
            asic_count =  board.get('asic_count', 0)
            if not asic_count:
                 raise ValueError('Invalid asic count for {}!'.format(board_name))
            board_id_offset = board.get('board_id_offset', -1)
            if not (board_id_offset >= 0):
                 raise ValueError('Invalid board id offset for {}!'.format(board_name))
            chip_type =  board.get('asic', None)

            board_id_list[board_name] = self._get_board_id_from_offset(board_id_offset)

        return board_id_list

    def get_sku_ids_for_target_chip(self):
        sku_ids = dict()
        if 'emu' in (self.target_machine):
            hwcap_code_gen = HWCAPCodeGen(self.input_dir, self.output_dir,
                                      self.target_chip, self.target_machine)
            sku_ids.update(hwcap_code_gen.get_emu_sku_ids_with_sbp(all_target_chips=False))
        else:
            sku_ids.update(self.get_fungible_board_sku_ids(all_target_chips=False))

        return sku_ids

    def get_header_file_list(self):
        return [self.sku_file_prefix + '.h']

    # Generates sku id files
    def generate_code(self):
        date = datetime.datetime.now()
        this_dir = os.path.dirname(os.path.abspath(__file__))
        meta_data = {
            'date' : date.strftime("%x"),
            'year' : date.year,
            'generator' : os.path.basename(os.path.abspath(__file__)),
            'filename_prefix': self.sku_file_prefix
        }

        all_fungible_board_skus = \
                self.get_fungible_board_sku_ids(all_target_chips=True)
        hwcap_code_gen = HWCAPCodeGen(self.input_dir, self.output_dir,
                                      self.target_chip, self.target_machine)
        all_emu_skus = \
                hwcap_code_gen.get_emu_sku_ids(all_target_chips=True)

        fun_board_skus = self.get_fungible_board_sku_ids(False)
        fun_board_list = self.get_fungible_board_ids()

        emu_skus = hwcap_code_gen.get_emu_sku_ids(all_target_chips=False)

        if emu_skus is None:
            raise argparse.ArgumentTypeError('emu_sku config is empty!')

        if fun_board_skus is None or all_fungible_board_skus is None:
            raise argparse.ArgumentTypeError('fungible boards list is empty!')

        env = Environment(loader=FileSystemLoader(this_dir))
        tmpl = env.get_template(self.sku_h_tmpl)
        header_file = self.sku_file_prefix + '.h'
        output_file = os.path.join(self.output_dir, header_file)
        board_id_start = 0x0001 << 0x8
        with open (output_file, 'w') as f:
            f.write(tmpl.render(
                emu_sku_list=all_emu_skus,
                fun_board_sku_list=all_fungible_board_skus,
                fun_board_list=fun_board_list,
                board_id_start=board_id_start,
                meta_data=meta_data))

        tmpl = env.get_template(self.sku_c_tmpl)
        c_file = self.sku_file_prefix + '.c'
        output_file = os.path.join(self.output_dir, c_file)
        with open (output_file, 'w') as f:
            f.write(tmpl.render(
                emu_sku_list=all_emu_skus,
                fun_board_sku_list=all_fungible_board_skus,
                meta_data=meta_data))

    # generate the version 1 data, most of which is a PCI config
    def _get_version1_data(self, pci_cfg_dir, sku_name, flags=0):
        if not pci_cfg_dir:
            return b''

        # try reading a file based on sku_name
        file_name = os.path.join(pci_cfg_dir, 'pcicfg-' + sku_name + '.bin')
        try:
            with open(file_name, 'rb') as f:
                pci_config = f.read()
        except:
            return b''

        # generate the version 1 filler data (struct puf_rom_eeprom_image_s)
        bytes = struct.pack("<I", 1)      # uint32_t version = 1
        bytes += b'EEPRMIMG'              # uint64_t magic
        bytes += struct.pack("<Q", flags) # uint64_t flags
        bytes += struct.pack("<I", 0)     # uint32_t hw_rev
        bytes += struct.pack("<I", 0)     # uint32_t board_subtype
        bytes += pci_config

        return bytes


    # generate uniform eeprom file filenames
    def eeprom_filename(self, sku_name):
        return 'eeprom_{}'.format(sku_name)

    def flag_variants_for_chip(self, chip):
        # If there's no entries in the variants table, just use
        # the default sku with flags == 0;
        DEFAULT_FLAG_VAR = [("", 0)]
        return CHIP_FLAG_EEPR_VARIANTS.get(chip, DEFAULT_FLAG_VAR)

    def write_eepr_file_data(self, sku_var, sku_name, sku_id,
                             pci_cfg_dir, flags):
        # filename for the flag variant
        fname = self.eeprom_filename(sku_var)
        # PCI data for the SKU
        version1_data = self._get_version1_data(pci_cfg_dir, sku_name, flags)
        abs_eeprom_file_path = os.path.join(self.output_dir, fname)
        with open(abs_eeprom_file_path, "wb") as f:
            byte_array = struct.pack('<I', sku_id) + version1_data
            f.write(byte_array)

        return { 'filename' : fname, 'image_type': sku_var }

    def write_eepr_files(self, sku_name, sku_id, pci_cfg_dir):
        dentries = {}
        chip = self.get_chip_for_sku_id(sku_name)

        # write out a file for each flag variant
        flagvars = self.flag_variants_for_chip(chip)
        for (suffix, flags) in flagvars:
            skuvar = "{}{}".format(sku_name, suffix)
            dent = self.write_eepr_file_data(skuvar, sku_name, sku_id,
                                             pci_cfg_dir, flags)
            dentries[sku_name] = dent

        return dentries

    # Generates eeprom files for the emulation builds with SBP and fungible boards
    def generate_eeprom(self):
        all_board_skus_with_sbp = \
                self.get_fungible_board_sku_ids(all_target_chips=True)
        hwcap_code_gen = HWCAPCodeGen(self.input_dir, self.output_dir,
                                      self.target_chip, self.target_machine)
        emu_skus_with_sbp = \
                hwcap_code_gen.get_emu_sku_ids_with_sbp(all_target_chips=True)

        all_skus_with_sbp = dict(all_board_skus_with_sbp)
        all_skus_with_sbp.update(emu_skus_with_sbp)

        # empty dict for json list file
        eeprom_dict = {}

        # figure out the path to the pcicfg files generated by FunOS
        pci_cfg_dir = None
        if self.sdk_dir:
            pci_cfg_dir = os.path.join(self.sdk_dir, 'feature_sets', 'pcicfg')
            if not os.path.isdir(pci_cfg_dir):
                pci_cfg_dir = None

        for sku_name, sku_id in all_skus_with_sbp.iteritems():
            fnd = self.write_eepr_files(sku_name, sku_id, pci_cfg_dir)
            eeprom_dict.update(fnd)

        # write out the list of eeprom files as a dict
        with open(os.path.join(self.output_dir, 'eeprom_list.json'), "wb") as f:
            json.dump(eeprom_dict, f, indent=4)


    # Generates json lists of eeprom files for each chip
    def generate_chip_eeprom_lists(self):
        chips_seen = []
        fun_board_config = self._get_fungible_board_id_config()
        for board in fun_board_config:
            chip_type = board.get('asic', None)
            
            # skip seen chips
            if chip_type in chips_seen:
                continue

            chips_seen.append(chip_type)
            self.target_chip = chip_type

            all_board_skus_with_sbp = \
                    self.get_fungible_board_sku_ids(all_target_chips=False)

            eeprom_list = {}
            for sku_name, sku_id in all_board_skus_with_sbp.iteritems():
                for (suffix, _) in self.flag_variants_for_chip(chip_type):
                    sku_var = sku_name + suffix
                    eeprom_list[sku_var] = {
                        'filename' : self.eeprom_filename(sku_var),
                        'image_type' : sku_var
                    }

                    try:
                        eeprom_list[sku_var]['hw_base'] = \
                            filter(lambda x: x['name'] == sku_name and x['asic'] == chip_type,
                                fun_board_config)[0]['hw_base']
                    except:
                        pass

                with open(os.path.join(self.output_dir, '{}_eeprom_list.json'.format(chip_type)), "wb") as f:
                    json.dump(eeprom_list, f, indent=4)

    # Generate a new dict containing @entry that can be merged into
    # a global config for a given sku
    @staticmethod
    def create_sku_cfg_entry(sku, entry):
        return { 'skus' : { sku: entry }}

    # Get a dict key where the sku entries are stored
    @staticmethod
    def get_sku_path():
        return 'skus'

    @staticmethod
    def get_build_deplist():
        this_dir = os.path.dirname(os.path.abspath(__file__))
        templates = (SKUCfgGen.sku_h_tmpl, SKUCfgGen.sku_c_tmpl)
        return [os.path.join(this_dir, tmpl) for tmpl in templates]
