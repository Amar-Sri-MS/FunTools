#!/usr/bin/env python3

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
        try:
            cl_json = jsonutils.load_fungible_json(file_name)
        except:
            logger.error("Failed to read file: {}".format(file_name))
            raise

        return cl_json


    def get_board_layer_config(self, board):
        """Returns the board layer configuration in json format
        """
        # Read the board layer config and convert it to json
        file_name = self.input_dir + '/sku_config/defaults'
        file_name += '/board_layer_%s.cfg' % board
        try:
            bl_json = jsonutils.load_fungible_json(file_name)
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

    def get_perst_bl(self, hu, hu_ctl, ctl, bl_json):
        """get the perst parameters for the given controller specified
        by its hu, hu_ctl from bl_json
        """
        mode = ctl['mode']
        width = ctl['pcie_width']

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
        return perst

    def apply_perst(self, sku_json, bl_json, cl_json):
        """Assign the PERST parameters to each PCIe controller
        """
        # Skip processing if perst config is not available
        if not 'perst' in bl_json:
            return sku_json

        # Get the list of PCIe controllers
        controllers = sku_json['skus'][self.board_name]['HuInterface']['HostUnitController']

        # Assign the PERST to each controller
        for hostunit in controllers:
            if '_args' in hostunit:
                ctl = hostunit
                hu = ctl['_args'][0];
                hu_ctl = ctl['_args'][1];

                # Only physical HUs can have PERST signals
                if (hu >= cl_json['chip_params']['hsu_max']):
                    continue

                # Add the perst configuration to the PCIe controller
                ctl['perst'] = self.get_perst_bl(hu, hu_ctl, ctl, bl_json)
            else:
                hu_number = hostunit.split("_")
                hu = int(hu_number[1])
                value = controllers[hostunit]
                for controller in value:
                    ctl_number = controller.split('_')
                    hu_ctl = int(ctl_number[1])
                    ctl = value[controller]

                    # Only physical HUs can have PERST signals
                    if (hu >= cl_json['chip_params']['hsu_max']):
                        continue

                    # Add the perst configuration to the PCIe controller
                    ctl['perst'] = self.get_perst_bl(hu, hu_ctl, ctl, bl_json)

        return sku_json


    def apply_non_perst(self, sku_json, bl_json, def_cfg, sku_overrides_board=True):
        """Write the remaining board layer configuration to the SKU file
        """
        default_cfg_gen = DefaultCfgGen(self.input_dir, self.target_chip)

        tmp_bl_json = bl_json.copy()

        # Perst is processed elsewhere so remove it
        if 'perst' in tmp_bl_json:
            del tmp_bl_json['perst']

        # Nothing to do if the board layer is empty
        if not bool(tmp_bl_json):
            return tmp_bl_json if sku_overrides_board else sku_json

        # Rename the board name placeholder with the real board name
        tmp_bl_json['skus'][self.board_name] = tmp_bl_json['skus']['board']
        del tmp_bl_json['skus']['board']

        # Apply defaults to the board layer configuration file
        default_cfg_gen.apply_defaults(tmp_bl_json, def_cfg)

        if sku_overrides_board:
            return jsonutils.merge_dicts_recursive(tmp_bl_json, sku_json)
        else:
            return jsonutils.merge_dicts_recursive(sku_json, tmp_bl_json)


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
            return sku_json

        final_override_json = dict()

        if isinstance(self.board_layer_name, dict):
            self.board_layer_name = self.board_layer_name[self.target_chip]

        if not isinstance(self.board_layer_name, list):
            self.board_layer_name = [ self.board_layer_name ]

        for board in self.board_layer_name:
            # Get the board layer config
            logger.info('Processing {}'.format(board))
            bl_json = self.get_board_layer_config(board)

            # Generate a "common" board layer based on all layers,
            # ensuring that any board layer that follows, overrides any
            # matching settings from a previous layer.
            final_override_json = self.apply_non_perst(final_override_json, bl_json,
                def_cfg, sku_overrides_board=False)

        # Apply sku config on top of the complete board layer json
        sku_json = jsonutils.merge_dicts_recursive(final_override_json, sku_json)

        for board in self.board_layer_name:
            # Get the board layer config
            logger.info('Processing {}'.format(board))
            bl_json = self.get_board_layer_config(board)

            # Get the chip layer config
            cl_json = self.get_chip_layer_config()

            # Apply the perst board values to the SKU config file
            sku_json = self.apply_perst(sku_json, bl_json, cl_json)

        # If we had a per-chip layer selection, then strip the per-chip dict
        # and only leave the valid values for a given chip
        if isinstance(sku_json['skus'][self.board_name]['PlatformInfo']['board_layer'], dict):
            sku_json['skus'][self.board_name]['PlatformInfo']['board_layer'] = \
                sku_json['skus'][self.board_name]['PlatformInfo']['board_layer'][self.target_chip]

        return sku_json
