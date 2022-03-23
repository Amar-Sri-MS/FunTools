#!/usr/bin/env python3

# This script is to validate the FUNLOG_MANIFEST file based on
# Log Archives Proposal. The script requires the directory path
# where the manifest file is located and prints validation messages
# and final status whether the validation succeeded or not.
#
# An example run:
# (.venv) ✗ python manifest_validator.py ~/techsupport
# Parsing manifest file at /Users/sourabhjain/techsupport/FUNLOG_MANIFEST
# VALIDATION STATUS: SUCCESS
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import argparse
import logging

from . import manifest_parser


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Manifest file directory')

    args = parser.parse_args()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    is_valid = validate(args.dir)

    if is_valid:
        logging.info(f'VALIDATION STATUS: SUCCESS')
    else:
        logging.info(f'VALIDATION STATUS: FAILED')


def validate(path):
    """ Validates a manifest file within the given directory path """
    manifest = manifest_parser.parse(path)
    is_valid = True

    # Check if the manifest is empty
    if not manifest:
        logging.error('Manifest file is empty')
        return False        

    # Check if the manifest file contains contents
    contents = manifest.get('contents')
    if not contents:
        logging.error('Manifest file does not contain contents')
        is_valid = False

    # Check the contents of the manifest file
    for index, content in enumerate(contents, start=1):
        try:
            frn_info = manifest_parser.parse_FRN(content)
            if not content.startswith('frn'):
                logging.warning(f'Manifest content string at line #{index} does not start with frn')

            # Check if required fields are present
            if not frn_info.get('resource_type'):
                logging.error(f'Manifest content at line #{index} does not contain value for resource_type')
                is_valid = False

            if not frn_info.get('prefix_path') and not frn_info.get('sub_path'):
                logging.error(f'Manifest content at line #{index} does not contain value for prefix_path and sub_path')
                is_valid = False

            for key, value in list(frn_info.items()):
                if not value:
                    logging.warning(f'Manifest content at line #{index} does not contain value for {key}')

        except:
            logging.error(f'Manifest content string at line #{index} is not in a correct format')
            is_valid = False

    return is_valid


if __name__ == "__main__":
    main()