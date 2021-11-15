#!/usr/bin/env python3

# 
# Getting the config from config file
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved. 


import json
import logging
import os
import sys


def get_config():
    """
    Returns the config after reading the config file.
    Merges config.json with default_config.json to return
    the config dict.
    """
    config = {}
    try:
        file_path = os.path.abspath(os.path.dirname(__file__))
        config_path = os.path.join(file_path, 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
    except IOError:
        logging.warning('Config file not found! Checking for default config file..')

    try:
        default_config_path = os.path.join(file_path, 'default_config.json')
        with open(default_config_path, 'r') as f:
            default_config = json.load(f)
        # Overriding default config with custom config
        config = { **default_config, **config }
    except IOError:
        logging.error('Default config file not found!')
        sys.exit('Default config file not found! Exiting..')

    return config