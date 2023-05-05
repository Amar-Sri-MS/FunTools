#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""Utilities for C code generation from emulation hwcap JSON config
"""

import glob, os, sys, datetime
import logging
from pprint import pprint
import tempfile
import json
import jsonutils
from itertools import chain
import argparse

logger = logging.getLogger('hwcap_gen')
logger.setLevel(logging.INFO)

class HWCAPDataCatalog():
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir

        self.hw_block_inst_cnts = dict()
        self.hwcap_data_catalog = dict()
        self.hw_block_defs = dict()
        self.emu_sku_ids = dict()

        hwcap_schema  = os.path.join(
            self.input_dir, 'hwcap_config/hwcap_schema.cfg')
        logger.debug('Processing hwcap catalog: {}'.format(hwcap_schema))
        self.hwcap_data_catalog = jsonutils.load_fungible_json(hwcap_schema)

        for k, v in list(self.hwcap_data_catalog.get('hw_blocks', None).items()):
            self.hw_block_inst_cnts[k] = v["inst_cnt"]
            info = v["info"]
            sub_blocks = dict()
            for element in info:
                if type(element) is dict:
                    sub_blocks.update(element)
                else:
                    sub_blocks.update({element:1})
            self.hw_block_defs[k] = sub_blocks

        emu_sku_cfg_file  = os.path.join(
            self.input_dir, 'hwcap_config/emu_sku_ids.cfg')
        logger.debug('Processing emulation sku ids file: {}'.format(
            emu_sku_cfg_file))
        self.emu_sku_ids = jsonutils.load_fungible_json(emu_sku_cfg_file)

    def _get_hwcap_data_catalog(self):
        return self.hwcap_data_catalog

    def _get_valid_block_status_list(self):
        return self.hwcap_data_catalog.get('block_status', None)

    def _get_hw_block_defs(self):
        return self.hw_block_defs

    def _get_hw_block_inst_cnts(self):
        return self.hw_block_inst_cnts

    def _get_hw_sub_block_defs(self, block):
        return self.hw_block_defs.get(block, None)

    def get_emu_valid_sku_list(self):
        return self.emu_sku_ids.get('emu_skus', None)

    def get_max_emu_sku_id(self):
        max_sku_id = 0
        for sku_name,sku_id in self.get_emu_valid_sku_list().items():
            if sku_id > max_sku_id:
                max_sku_id = sku_id
        return max_sku_id


class HWCAPCodeGen():
    gen_file_prefix = 'hwcap_config'
    gen_cfg_name = 'hwcap'
    hwcap_h_tmpl = 'hwcap_config_h.j2'
    hwcap_c_tmpl = 'hwcap_config_c.j2'

    def __init__(self, input_dir, output_dir,
                 target_chip, target_machine):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.target_chip = target_chip
        self.target_machine = target_machine
        self.hwcap_catalog = HWCAPDataCatalog(input_dir, output_dir)

    #Generate hwcap c header file for the config data catalog
    def _generate_hwcap_cfg_header_file(self, include_files):
        import jinja2
        hw_block_inst_cnts = self.hwcap_catalog._get_hw_block_inst_cnts()
        hw_block_defs = self.hwcap_catalog._get_hw_block_defs()
        hw_block_status_list = self.hwcap_catalog._get_valid_block_status_list()
        date = datetime.datetime.now()
        this_dir = os.path.dirname(os.path.abspath(__file__))
        metadata = {
            'date' : date.strftime("%x"),
            'year' : date.year,
            'generator' : os.path.basename(os.path.abspath(__file__)),
            'filename_prefix': self.gen_file_prefix
        }

        env = jinja2.Environment(loader=jinja2.FileSystemLoader(this_dir))
        tmpl = env.get_template(self.hwcap_h_tmpl)
        header_file = self.gen_file_prefix + '.h'
        output_file = os.path.join(self.output_dir, header_file)
        with open (output_file, 'w') as f:
            f.write(tmpl.render(
                hw_block_status_list=hw_block_status_list,
                hw_block_inst_cnts=hw_block_inst_cnts,
                hw_block_defs=hw_block_defs,
                include_files=include_files,
                hwcap_max_entries=self.hwcap_catalog.get_max_emu_sku_id(),
                metadata=metadata))

    # Returns all hw capabilities config
    def _get_hwcap_config(self, all_target_chips=False):
        hwcap_cfg = dict()
        patterns = list()

        if all_target_chips:
            for chip in ('f1', 's1', 'f1d1', 's2', 'f2'):
                patterns.append(f'hwcap_config/{chip}_emu_skus/*.cfg')
        elif self.target_chip:
            patterns.append(f'hwcap_config/{self.target_chip}_emu_skus/*.cfg')

        if len(patterns) == 0:
            raise argparse.ArgumentTypeError(
                'Empty hwcap: all_target_chips:{} target_chip: {}!'.format(
                    all_target_chips, self.target_chip))

        for pattern in patterns:
            for cfg in glob.glob(os.path.join(self.input_dir, pattern)):
                logger.debug('Processing hwcap config:{}'.format(cfg))
                cfg_json = jsonutils.load_fungible_json(cfg)
                hwcap_cfg = jsonutils.merge_dicts(hwcap_cfg, cfg_json)

        hwcap_cfg = hwcap_cfg.get('skus', None)

        return hwcap_cfg

    # Checks the per sku per block data with schema
    def _hw_block_data_finalise(self, hw_block_name, hw_block_cfg):
        sub_blocks = self.hwcap_catalog._get_hw_sub_block_defs(hw_block_name)
        hw_block_status_list = self.hwcap_catalog._get_valid_block_status_list()

        for entry,value in hw_block_cfg.items():
            if not entry in list(sub_blocks.keys()):
                raise argparse.ArgumentTypeError(
                    'hw block: {} entry: {} is not valid! valid list: {}'.format(
                        hw_block_name, entry, list(sub_blocks.keys())))
            entry_size = sub_blocks.get(entry, 0)
            entry_max_plus_1 = 0
            if entry_size:
                entry_max_plus_1 = 0x1 << entry_size
            if entry == 'status':
                if value not in hw_block_status_list:
                    raise argparse.ArgumentTypeError(
                        'hw block: {} entry: {} value:{} is not valid!'.format(
                            hw_block_name, entry, value))
            else:
                if not type(value) is int:
                    raise argparse.ArgumentTypeError(
                        'hw block: {} entry: {} value:{} is not valid!'.format(
                            hw_block_name, entry, value))
                if value >= entry_max_plus_1:
                    raise argparse.ArgumentTypeError(
                        'hw block: {} entry: {} value:{} is out of range!'.format(
                            hw_block_name, entry, value))

    # Check the config data consistancy
    def _per_sku_cfg_finalise(self, sku_name, per_sku_data):
        valid_skus = self.hwcap_catalog.get_emu_valid_sku_list()

        if not sku_name in list(valid_skus.keys()):
            raise argparse.ArgumentTypeError(
                'sku_name: {} is not valid! Valid list: {}'.format(
                    sku_name, list(valid_skus.keys())))

        per_sku_cfg = per_sku_data.get('hwcap', None)
        logger.debug('Finalising sku: {}'.format(sku_name))
        block_names = list(self.hwcap_catalog._get_hw_block_defs().keys())

        finalised_cfg = dict()
        for block, block_data in per_sku_cfg.items():
            if block not in block_names:
                raise argparse.ArgumentTypeError(
                    'hw block: {} is not a valid block'.format(block))
            block_inst_count = self.hwcap_catalog._get_hw_block_inst_cnts().get(block, 0)
            if not type(block_data) is list:
                block_data = [block_data]
                per_sku_cfg[block] = block_data
            block_inst_cfg = dict()
            for block_entry in block_data:
                id_range_str = block_entry.get('id', None)
                if block_inst_count > 1 and id_range_str is None:
                    raise argparse.ArgumentTypeError(
                        'sku: {} hw block: {} should have id'
                        ' key!'.format(sku_name, block))
                block_inst_list = list()
                if id_range_str:
                    block_inst_list = jsonutils.rangeexpand(
                        block_entry.get('id', None))
                    block_entry['id'] = block_inst_list
                for block_inst in block_inst_list:
                    if block_inst >= block_inst_count or block_inst < 0:
                        raise argparse.ArgumentTypeError(
                            'hw block: {} inst: {} is not valid!'.format(
                                block, block_inst))
                sub_blocks = block_entry.get('info', None)
                self._hw_block_data_finalise(block, sub_blocks)
        return per_sku_cfg

    #Generate hwcap c file for the config data
    def _generate_hwcap_cfg_c_file(self):
        import jinja2
        hw_block_inst_cnts = self.hwcap_catalog._get_hw_block_inst_cnts()
        hw_block_defs = self.hwcap_catalog._get_hw_block_defs()
        hw_block_status_list = self.hwcap_catalog._get_valid_block_status_list()
        date = datetime.datetime.now()
        this_dir = os.path.dirname(os.path.abspath(__file__))
        metadata = {
            'date' : date.strftime("%x"),
            'year' : date.year,
            'generator' : os.path.basename(os.path.abspath(__file__)),
            'filename_prefix': self.gen_file_prefix
        }

        all_skus_hwcap_cfg = self._get_hwcap_config(all_target_chips=False)
        finalised_cfg = dict()
        for sku_name,per_sku_cfg in all_skus_hwcap_cfg.items():
            cfg = self._per_sku_cfg_finalise(sku_name, per_sku_cfg)
            finalised_cfg[sku_name] = cfg

        env = jinja2.Environment(loader=jinja2.FileSystemLoader(this_dir))
        env.lstrip_blocks = True
        c_file =  self.gen_file_prefix + ".c"
        tmpl = env.get_template(self.hwcap_c_tmpl)
        header_file = self.gen_file_prefix + '.h'
        output_file = os.path.join(self.output_dir, c_file)
        with open (output_file, 'w') as f:
            f.write(tmpl.render(
                hwcap_cfg=finalised_cfg,
                metadata=metadata))

    # Returns the emulation sku ids of the target chip
    def get_emu_sku_ids(self, all_target_chips = False):
        all_valid_skus = self.hwcap_catalog.get_emu_valid_sku_list()
        if all_target_chips:
            return all_valid_skus

        emu_sku_ids = list(self._get_hwcap_config(all_target_chips).keys())
        emu_skus = dict()
        for sku in emu_sku_ids:
            if not sku in all_valid_skus:
                raise argparse.ArgumentTypeError(
                    'Invalid sku: {}! Valid list: {}'.format(
                        sku, all_valid_skus))
            emu_skus[sku] = all_valid_skus[sku]

        return emu_skus

    def get_emu_sku_ids_with_sbp(self, all_target_chips = False):
        emu_skuids = self.get_emu_sku_ids(all_target_chips)
        hwcap_config = self._get_hwcap_config(all_target_chips)
        for sku in list(emu_skuids.keys()):
            try:
                sku_cfg = hwcap_config.get(sku, None).get('hwcap', None)
            except:
                logger.error("Error processing config for sku: {}".format(sku))
                raise
            sbp_cfg = sku_cfg.get('sbp', None)
            sbp_valid = 0
            if sbp_cfg:
                sbp_valid = sbp_cfg.get('info', None).get('valid', 0)
            if not sbp_valid:
                emu_skuids.pop(sku)
        return emu_skuids

    def generate_code(self, include_files):
        self._generate_hwcap_cfg_header_file(include_files)
        self._generate_hwcap_cfg_c_file()

    @staticmethod
    def get_build_deplist():
        this_dir = os.path.dirname(os.path.abspath(__file__))
        templates = (HWCAPCodeGen.hwcap_h_tmpl, HWCAPCodeGen.hwcap_c_tmpl)
        return [os.path.join(this_dir, tmpl) for tmpl in templates]
