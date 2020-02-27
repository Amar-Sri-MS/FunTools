#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""Utilities for nu config
"""

import glob, os, sys, datetime
from string import Template
import logging, sys
import tempfile
import json
import jsonutils
from itertools import chain

logger = logging.getLogger('nu_cfg_gen')
logger.setLevel(logging.INFO)

class NUCfgGen():
    def __init__(self, input_dir, output_dir,
		 target_chip, target_machine):
        self.input_dir = input_dir
        self.output_dir = output_dir
	self.target_chip = target_chip
	self.target_machine = target_machine

    def _nu_parser_handling(self, keyword1, keyword2, new_cfg, cfg):
	new_cfg[keyword1][keyword2] = new_cfg[keyword1][keyword2] + cfg[keyword1][keyword2]

    # Merge two dictionaries
    # If they have the same key, merge contents
    # This is necessary e.g. for the p1 peline:
    #       Both the PRS and FFE images fall under the "pipeline" key,
    #       so we need to merge them properly
    def _nu_merge_dicts(self, cfg1, cfg2):
	new_cfg = cfg1
	for key in list(cfg2.keys()):
	    if key in list(new_cfg.keys()):
		keyword1 = "pipeline"
		keyword2 = 'PARSER'
		if keyword1 == key and keyword2 in list(new_cfg[key].keys()) and keyword2 in list(cfg2[key].keys()):
		    self._nu_parser_handling(keyword1, keyword2, new_cfg, cfg2)
		else:
		    new_cfg[key].update(cfg2[key])
	    else:
		new_cfg[key] = cfg2[key]

	return new_cfg

    # Merges all nu csr replay config files
    def csr_replay_config_generate(self):
        nu_csr_replay_cfg = dict()

	for cfg in glob.glob(os.path.join(self.input_dir, 'nu_config/*csr*.cfg')):
	    logger.debug('Processing {}'.format(cfg))
            with open(cfg, 'r') as f:
                cfg_json = f.read()
                cfg_json = jsonutils.standardize_json(cfg_json)
                cfg_json = json.loads(cfg_json)
	        nu_csr_replay_cfg = self._nu_merge_dicts(
                    nu_csr_replay_cfg, cfg_json)
	return nu_csr_replay_cfg

    # Merges nu pipeline config
    def generate_config(self):
	nu_cfg = dict()

	for cfg in glob.glob(os.path.join(self.input_dir, 'nu_config/*.cfg')):
	    logger.debug('Processing {}'.format(cfg))
            with open(cfg, 'r') as f:
                cfg_json = f.read()
                cfg_json = jsonutils.standardize_json(cfg_json)
                cfg_json = json.loads(cfg_json)
	        nu_cfg = self._nu_merge_dicts(nu_cfg, cfg_json)
	return nu_cfg
