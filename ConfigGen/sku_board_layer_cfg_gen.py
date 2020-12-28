#!/usr/bin/env python

#This module applies the board layer to the SKU configuration

import os, sys, logging, glob
import copy
import json
import jsonutils
from default_cfg_gen import DefaultCfgGen

logger = logging.getLogger('sku_board_layer_cfg_gen')
logger.setLevel(logging.INFO)


class BoardLayer():
    board_name = ""
    board_layer_name = ""

    def __init__(self, input_dir, target_chip):
        self.input_dir = input_dir
        self.target_chip = target_chip


    def get_chip_layer_config(self):
        """Returns the chip layer configuration in json format
        """
        # Read the chip layer config and convert it to json
        file_name = self.input_dir + '/sku_config/defaults'
        file_name += '/chip_layer_%s.cfg' % self.target_chip
        with open(file_name, 'r') as f:
            cl_json = f.read()
            cl_json = jsonutils.standardize_json(cl_json)
            try:
                cl_json = json.loads(cl_json)
            except:
                logger.error("Failed to read file: {}".format(file_name))
                raise

        return cl_json


    def get_board_layer_config(self):
        """Returns the board layer configuration in json format
        """
        # Read the board layer config and convert it to json
        file_name = self.input_dir + '/sku_config/defaults'
        file_name += '/board_layer_%s.cfg' % self.board_layer_name
        with open(file_name, 'r') as f:
            bl_json = f.read()
            bl_json = jsonutils.standardize_json(bl_json)
            try:
                bl_json = json.loads(bl_json)
            except:
                logger.error("Failed to read file: {}".format(file_name))
                raise

        return bl_json


    def get_perst(self, hu, ctl, mode, width, connector, bl_json):
        """Return the perst parameters for the given controller specified
        by its hu, ctl, mode, width and connector.
        """
        # Search for the controller in the board layer configuration
        for perst in bl_json['perst']:
            if (perst['hu'] == hu and perst['ctl'] == ctl and
                perst['mode'] == mode and perst['width'] == width):
                # The connector is optional, only check if non empty
                if (connector):
                    if perst['connector'] != connector:
                        continue

                # Found it
                return perst['perst']
        return {}


    def apply_perst(self, sku_json, bl_json, cl_json):
        """Assign the PERST parameters to each PCIe controller
        """
        # Get the list of PCIe controllers
        controllers = sku_json['skus'][self.board_name]['HuInterface']['HostUnitController']

        # Assign the PERST to each controller
        for ctl in controllers:
            hu = ctl['_args'][0];
            hu_ctl = ctl['_args'][1];
            mode = ctl['mode']
            width = ctl['pcie_width']

            # Only physical HUs can have PERST signals
            if (hu >= cl_json['chip_params']['hsu_max']):
                continue

            # DNSW means the controller is in RC mode.
            # UPSW means the controller is in EP mode.
            if (mode == 'DNSW'):
                mode = 'RC'
            elif (mode == 'UPSW'):
                mode = 'EP'

            # The connector is optional (only needed for PCIe controller
            # attached to a target via cabling. Can be removed after getting its
            # value
            connector = ctl.get('connector', '')
            if connector:
                del ctl['connector']

            perst =  self.get_perst(hu, hu_ctl, mode, width, connector,
                                    bl_json)

            # If perst is not found for the controller, stop!
            if not perst:
                raise Exception("Perst not found for hu=%d ctl=%d board=%s"
                                % (hu, hu_ctl, self.board_name))

            # Add the perst configuration to the PCIe controller
            ctl['perst'] = perst
        return sku_json


    def apply_rest(self, sku_json, bl_json, def_cfg):
        """Write the remaining board layer configuration to the SKU file
        """
        tmp_bl_json = dict()
        default_cfg_gen = DefaultCfgGen(self.input_dir, self.target_chip)

        tmp_bl_json = bl_json

        # Perst is processed elsewhere so remove it
        del tmp_bl_json['perst']

        # Nothing to do if the board layer is empty
        if not bool(tmp_bl_json):
            return

        # Rename the board name placeholder with the real board name
        tmp_bl_json['skus'][self.board_name] = tmp_bl_json['skus']['board']
        del tmp_bl_json['skus']['board']

        # Apply defaults to the board layer configuration file
        default_cfg_gen.apply_defaults(tmp_bl_json, def_cfg)

        # Merge the board layer configuration with the SKU file
        sku_json = jsonutils.merge_dicts_recursive(tmp_bl_json, sku_json)

    def apply_board_layer(self, sku_json, def_cfg):
        """Apply the board layer configuration, when available, to a SKU file.
        """
        bl_json = dict()
        cl_json = dict()

        # Extract the name of the board out the SKU config file
        for key in list(sku_json['skus'].keys()):
            self.board_name = key
            break

        # Extract the name of the board layer out the SKU config file
        plat_info = sku_json['skus'][self.board_name]['PlatformInfo']
        self.board_layer_name = plat_info.get('board_layer', "")

        # Check the board layer was specified
        if not self.board_layer_name:
            return

        # Get the board layer config
        logger.info('Processing {}'.format(self.board_name))
        bl_json = self.get_board_layer_config()

        # Get the chip layer config
        cl_json = self.get_chip_layer_config()

        # Apply the perst board values to the SKU config file
        self.apply_perst(sku_json, bl_json, cl_json)

        # Apply the rest of the board values to the SKU config file
        self.apply_rest(sku_json, bl_json, def_cfg)
