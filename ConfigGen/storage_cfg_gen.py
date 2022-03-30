#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""Utilities for storage config
"""

import glob, os, sys, datetime
from string import Template
import logging, sys
import tempfile
import json
import jsonutils
from itertools import chain

logger = logging.getLogger('storage_cfg_gen')
logger.setLevel(logging.INFO)

class StorageCfgGen():
    def __init__(self, input_dir, output_dir,
                 target_chip, target_machine):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.target_chip = target_chip
        self.target_machine = target_machine

    # Merges storage config
    def generate_config(self):
        storage_cfg = dict()

        for cfg in glob.glob(os.path.join(self.input_dir, 'storage_config/*.cfg')):
            logger.debug('Processing {}'.format(cfg))
            with open(cfg, 'r') as f:
                cfg_json = f.read()
                cfg_json = jsonutils.standardize_json(cfg_json)
                cfg_json = json.loads(cfg_json)
                storage_cfg = jsonutils.merge_dicts(storage_cfg, cfg_json)
        return storage_cfg
