#!/usr/bin/env python3

# This module generates the default dictionary which contains blocks of
# parameters/values. Each of these blocks can then be used by SKU files as
# default configuration.
#
# The produced default dictionary has the following format:
#
# def_cfg : {
#     name1 : {
#         key1 : value1,
#         key2 : value2,
#         keyn : valuen
#     },
#
#     name2 : {
#         key1 : value1,
#         key2 : value2,
#         keyn : valuen
#     },
#
#     namen : {
#         key1 : value1,
#         key2 : value2,
#         keyn : valuen
#     },
# }
#
# Where:
#     namex:            It's s a block of parameters/values.
#                       The blocks' contents are defined in default
#                       configuration files by entries with the prefix
#                       "DEFAULT_".
#                       Namex matches the entry name, but with prefix "DEFAULT_"
#                       removed.
#
#     keyx:             A configuration parameter.
#
#     valuex:           A configuration parameter value.
#


import os, sys, logging, glob
import copy
import json
import jsonutils
from collections.abc import Mapping

logger = logging.getLogger('cfg_gen')
logger.setLevel(logging.INFO)

class DefaultCfgGen():
    def __init__(self, input_dir, target_chip):
        self.input_dir = input_dir
        self.target_chip = target_chip

    def build_default_entry(self, def_json, entry):
        """Recursively expand an entry.
        """
        for key in entry.copy():
            # Walk all the dictionaries in the entry recursively.
            if type(entry[key]) is dict:
                self.build_default_entry(def_json, entry[key])
                # At this point entry[key] is a leaf dictionary.
                if key in list(def_json.keys()):
                    # Apply defaults to entry[key] via sub_entry
                    sub_entry = {}
                    sub_entry.update(def_json[key])
                    sub_entry.update(entry[key])
                    # Expand the newly added defaults in entry[key]
                    self.build_default_entry(def_json, sub_entry)

                    # At this point sub_entry is a leaf dictionary with all the
                    # defaults applied/expanded. Replace entry[key] with it.
                    # First delete entry[key]
                    del entry[key]
                    # Second apply overrides
                    sub_entry.update(entry)
                    # Third replace it
                    entry.update(sub_entry)

    def process_default_file(self, def_json, def_cfg):
        """Only expand and add keys prefixed with "DEFAULT_" to the default
        dictionary.
        """
        for def_key, val in list(def_json.items()):
            # Only process keys prefixed with "DEFAULT_"
            if 'DEFAULT_' in def_key:
                # Build the entry.
                entry = {}
                entry = copy.deepcopy(def_json[def_key])
                self.build_default_entry(def_json, entry)

                # Save the entry
                new_key = def_key.replace('DEFAULT_', '')
                def_cfg[new_key] = entry

    def get_defaults(self):
        """Process all the default configuration files applicable to the given
        machine and generate the default dictionary.
        """
        def_cfg = dict()

        # These are the default configuration files
        file_patterns = [
            'sku_config/defaults/all_*.cfg',
            'sku_config/defaults/%s_*.cfg' % self.target_chip
        ]

        # Process every single default configuration file
        for file_pat in file_patterns:
            for def_file in glob.glob(os.path.join(self.input_dir, file_pat)):
                try:
                    def_json = jsonutils.load_fungible_json(def_file)
                except:
                    logger.error("Failed to load defaults file: {}".format(def_file))
                    raise

                self.process_default_file(def_json, def_cfg)

        return def_cfg

    def merge_entry(self, entry, cfg_json):
        """Modifies entry in place to contain values from cfg_json. If any value
        in entry is a dictionary, and the corresponding value in cfg_json is
        also a dictionary, then merge them in place.
        """
        for key, val_json in list(cfg_json.items()):
            val_entry = entry.get(key)
            if (isinstance(val_entry, Mapping) and
                 isinstance(val_json, Mapping)):
                self.merge_entry(val_entry, val_json)
            else:
                entry[key] = val_json

    def apply_defaults_to_config_entry(self, key, cfg_json, def_cfg):
        """Applies the defaults to an entry.
        """
        entry = copy.deepcopy(def_cfg[key])
        self.merge_entry(entry, cfg_json[key])
        del cfg_json[key]
        cfg_json.update(entry)

    def apply_defaults(self, cfg_json, def_cfg):
        """Traverse a configuration file recursevely looking for entries to
        apply default configuration to.
        """
        for key in cfg_json.copy():
            if type(cfg_json[key]) is dict:
                self.apply_defaults(cfg_json[key], def_cfg)
                if key in list(def_cfg.keys()):
                    self.apply_defaults_to_config_entry(key, cfg_json, def_cfg)
            elif type(cfg_json[key]) is list:
                for item in cfg_json[key]:
                    if type(item) is dict:
                        self.apply_defaults(item, def_cfg)
                        if key in list(def_cfg.keys()):
                            self.apply_defaults_to_config_entry(key, cfg_json, def_cfg)
