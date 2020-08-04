#!/usr/bin/env python

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
import collections
import copy
from sku_board_layer_cfg_gen import BoardLayer

logger = logging.getLogger('sku_cfg_gen')
logger.setLevel(logging.INFO)

class SKUCfgGen():
    sku_h_tmpl = 'platform_sku_h.j2'
    sku_c_tmpl = 'platform_sku_c.j2'
    sku_file_prefix = 'platform_sku'

    def __init__(self, input_dir, output_dir, target_chip, target_machine):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.target_chip = target_chip
        self.target_machine = target_machine

    def _get_fungible_board_id_config(self):
        board_id_cfg = dict()
        file_name = os.path.join(self.input_dir, 'sku_config/fungible_boards.cfg')
        logger.debug('Processing fungible boards file: {}'.format(file_name))
        with open(file_name, 'r') as f:
            cfg_json = f.read()
            cfg_json = jsonutils.standardize_json(cfg_json)
            board_id_cfg = json.loads(cfg_json)

        return board_id_cfg.get('fungible_boards', None)

    def build_default_config(self, def_json, def_cfg):
        for def_key, val in def_json.items():
            # Only keys prefixed with "DEFAULT_" are imported by board config
            # files. These must be expanded and saved in def_cfg.
            if 'DEFAULT_' in def_key:
                # Build the entry.
                entry = {}
                entry.update(def_json[def_key])
                for sub_key in list(val.keys()):
                    if def_json.has_key(sub_key):
                        sub_entry = {}
                        sub_entry.update(def_json[sub_key])
                        sub_entry.update(def_json[def_key][sub_key])
                        del entry[sub_key]
                        entry.update(sub_entry)
                # Save the entry
                new_key = def_key.replace('DEFAULT_', '')
                def_cfg[new_key] = entry

    def get_default_config(self, def_cfg):
        """Build a dictionary containing the default entries exported to board
        configuration files.
        """
        _path = 'sku_config/defaults/%s_*.cfg' % self.target_chip
        file_patterns = [_path]
        for file_pat in file_patterns:
            for def_file in glob.glob(os.path.join(self.input_dir, file_pat)):
                with open(def_file, 'r') as f:
                    def_json = f.read()
                    def_json = jsonutils.standardize_json(def_json)
                    try:
                        def_json = json.loads(def_json)
                    except:
                        logger.error("Failed to load defaults file: {}".format(def_file))
                        raise

                self.build_default_config(def_json, def_cfg)

    def merge_entry(self, entry, cfg_json):
        """Modifies entry in place to contain values from cfg_json. If any value
        in entry is a dictionary, and the corresponding value in cfg_json is
        also a dictionary, then merge them in place.
        """
        for key, val_json in cfg_json.items():
            val_entry = entry.get(key)
            if (isinstance(val_entry, collections.Mapping) and
                 isinstance(val_json, collections.Mapping)):
                self.merge_entry(val_entry, val_json)
            else:
                entry[key] = val_json

    def update_entry(self, key, cfg_json, def_cfg):
        """Applies the defaults to an entry.
        """
        entry = copy.deepcopy(def_cfg[key])
        self.merge_entry(entry, cfg_json[key])
        del cfg_json[key]
        cfg_json.update(entry)

    def apply_defaults_to_board_config(self, cfg_json, def_cfg):
        """Traverse the board configuration recursevely looking for entries to
        apply default configuration to.
        """
        for key, val in cfg_json.items():
            if type(val) is dict:
                self.apply_defaults_to_board_config(val, def_cfg)
                if key in list(def_cfg.keys()):
                    self.update_entry(key, cfg_json, def_cfg)
            elif type(val) is list:
                for item in val:
                    if type(item) is dict:
                        self.apply_defaults_to_board_config(item, def_cfg)
                        if key in list(def_cfg.keys()):
                            self.update_entry(key, cfg_json, def_cfg)

    def get_posix_or_emu_configs(self, board_cfg):
        """Get the configuration for all the posix or emulations that
        use the target chip.
        """
        def_cfg = dict()
        self.get_default_config(def_cfg)

        _path = 'sku_config/'

        if 'posix' in (self.target_machine):
            _path = _path + 'posix/%s_*.cfg' % self.target_chip
        else:
            _path = _path + 'emulation/%s_*.cfg' % self.target_chip

        file_patterns = [_path]
        logger.debug('board config paths: {}'.format(file_patterns))
        for file_pat in file_patterns:
            for cfg in glob.glob(os.path.join(self.input_dir, file_pat)):
                logger.debug('Processing per sku config: {}'.format(cfg))
                with open(cfg, 'r') as f:
                    cfg_json = f.read()
                    cfg_json = jsonutils.standardize_json(cfg_json)
                    try:
                        cfg_json = json.loads(cfg_json)
                    except:
                        logger.error("Failed to load config file: {}".format(cfg))
                        raise

                    self.apply_defaults_to_board_config(cfg_json, def_cfg)
                    board_cfg = jsonutils.merge_dicts(board_cfg, copy.deepcopy(cfg_json))

        return board_cfg

    def is_cfg_target_board(self, cfg_json):
        """Check if the configuration file is for the target
        being built.
        """
        for key in list(cfg_json['skus'].keys()):
            # First check the target chip
            if 'chip' not in cfg_json['skus'].get(key, {}).get('PlatformInfo', {}):
                continue
            chip = cfg_json['skus'][key]['PlatformInfo']['chip']
            if chip not in self.target_chip:
                return False
            # Next check the configuration file is for a board
            if 'machine' not in cfg_json['skus'].get(key, {}).get('PlatformInfo', {}):
                return False
            machine = cfg_json['skus'][key]['PlatformInfo']['machine']
            if machine != 'board':
                return False
            # Don't add the chip and machine keys to the output.
            del cfg_json['skus'][key]['PlatformInfo']['chip']
            del cfg_json['skus'][key]['PlatformInfo']['machine']
            return True

        return False

    def get_board_configs(self, board_cfg):
        """Get the configuration for all the boards that use the target
        chip.
        """
        def_cfg = dict()
        self.get_default_config(def_cfg)

        _path = 'sku_config/*/*.cfg'
        file_patterns = [_path]
        for file_pat in file_patterns:
            for cfg in glob.glob(os.path.join(self.input_dir, file_pat)):
                # Skip board layer files and defaults files
                if 'sku_config/defaults' in cfg:
                    continue
                logger.debug('Processing per sku config: {}'.format(cfg))
                with open(cfg, 'r') as f:
                    cfg_json = f.read()
                    cfg_json = jsonutils.standardize_json(cfg_json)
                    try:
                        cfg_json = json.loads(cfg_json)
                    except:
                        logger.error("Failed to load config file: {}".format(cfg))
                        raise

                    if not self.is_cfg_target_board(cfg_json):
                        continue

                    # Apply defaults to the board configuration
                    self.apply_defaults_to_board_config(cfg_json, def_cfg)

                    # Apply board layer configuration
                    board_layer = BoardLayer(self.input_dir, self.target_chip)
                    board_layer.apply_board_layer(cfg_json)

                    board_cfg = jsonutils.merge_dicts(board_cfg, copy.deepcopy(cfg_json))
        return board_cfg

    def get_additions(self, board_cfg, addition_machine):
        """Add addtional configuration if needed."""
        _path = 'sku_config/additions/%s/*.cfg' % self.target_chip
        file_patterns = [_path]
        logger.debug('Additional config paths: {}'.format(file_patterns))
        for file_pat in file_patterns:
            for cfg in glob.glob(os.path.join(self.input_dir, file_pat)):
                logger.debug('Processing per sku config: {}'.format(cfg))
                with open(cfg, 'r') as f:
                    cfg_json = f.read()
                    cfg_json = jsonutils.standardize_json(cfg_json)
                    try:
                        cfg_json = json.loads(cfg_json)
                    except:
                        logger.error("Failed to load config file: {}".format(cfg))
                        raise

                    # Check the additional file is for the machine being built
                    if 'machine' not in cfg_json['PlatformInfo'].keys():
                        continue
                    machine = cfg_json['PlatformInfo']['machine']
                    if machine != addition_machine:
                        continue;

                    # Remove the PlatformInfo key
                    del cfg_json['PlatformInfo']

                    board_cfg = jsonutils.merge_dicts(board_cfg, cfg_json)

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

    # Creates binary file with skuid
    def _create_binary_file(self, file_path, four_byte_data):
         with open(file_path, "wb") as f:
            byte_array = struct.pack('<I', four_byte_data)
            f.write(byte_array)

    # Generates eeprom files for the emulation builds with SBP and fungible boards
    def generate_eeprom(self):
        eeprom_filename = lambda sku_name: 'eeprom_{}'.format(sku_name)

        all_board_skus_with_sbp = \
                self.get_fungible_board_sku_ids(all_target_chips=True)
        hwcap_code_gen = HWCAPCodeGen(self.input_dir, self.output_dir,
                                      self.target_chip, self.target_machine)
        emu_skus_with_sbp = \
                hwcap_code_gen.get_emu_sku_ids_with_sbp(all_target_chips=True)

        all_skus_with_sbp = dict(all_board_skus_with_sbp)
        all_skus_with_sbp.update(emu_skus_with_sbp)

        eeprom_list = {}
        for sku_name, sku_id in all_board_skus_with_sbp.iteritems():
            eeprom_list[sku_name] = { 'filename' : eeprom_filename(sku_name) }

        with open(os.path.join(self.output_dir, 'eeprom_list.json'), "wb") as f:
            json.dump(eeprom_list, f, indent=4)

        for sku_name, sku_id in all_skus_with_sbp.iteritems():
            abs_eeprom_file_path = os.path.join(self.output_dir, eeprom_filename(sku_name))
            self._create_binary_file(abs_eeprom_file_path, sku_id)

    # Generates json lists of eeprom files for each chip
    def generate_chip_eeprom_lists(self):
        chips_seen = []
        fun_board_config = self._get_fungible_board_id_config()
        for board in fun_board_config:
            chip_type = board.get('asic', None)
            if chip_type not in chips_seen:
                chips_seen.append(chip_type)
                self.target_chip = chip_type

                eeprom_filename = lambda sku_name: 'eeprom_{}'.format(sku_name)

                all_board_skus_with_sbp = \
                        self.get_fungible_board_sku_ids(all_target_chips=False)

                eeprom_list = {}
                for sku_name, sku_id in all_board_skus_with_sbp.iteritems():
                    eeprom_list[sku_name] = { 'filename' : eeprom_filename(sku_name) }

                with open(os.path.join(self.output_dir, '{}_eeprom_list.json'.format(chip_type)), "wb") as f:
                    json.dump(eeprom_list, f, indent=4)

    @staticmethod
    def get_build_deplist():
        this_dir = os.path.dirname(os.path.abspath(__file__))
        templates = (SKUCfgGen.sku_h_tmpl, SKUCfgGen.sku_c_tmpl)
        return [os.path.join(this_dir, tmpl) for tmpl in templates]