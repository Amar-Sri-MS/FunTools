#!/usr/bin/env python3

#
# Parses Manifest file.
#

import logging
import os
import sys
import yaml

MANIFEST_FILE_NAME = 'FUNLOG_MANIFEST'


def parse(dir):
    """ Parse the manifest file inside the given directory """
    manifest = dict()
    try:
        manifest_path = os.path.join(dir, MANIFEST_FILE_NAME)
        logging.info(f'Parsing manifest file at {manifest_path}')
        with open(manifest_path) as manifest_file:
            manifest = yaml.safe_load(manifest_file)
        manifest = _format_manifest(manifest)
    except yaml.YAMLError as e:
        logging.exception('Could not parse the manifest file.')
    except FileNotFoundError as e:
        logging.warning('Could not find the manifest file.')
    return manifest


def _format_manifest(manifest):
    contents = list()
    for content in manifest['contents']:
        if type(content) == str:
            contents.append(content)

        # In case the last element of the FRN is empty, pyyaml
        # considers it a dict since the last character is :
        if type(content) == dict:
            frn = list(content.keys())[0]
            contents.append(f'{frn}:')

    manifest['contents'] = contents
    return manifest


def parse_FRN(frn_str):
    """ Parse FRN (Fungible Resource Name) into usable information """
    frn = frn_str.split(':')
    return {
        'namespace': frn[1],
        'system_type': frn[2],
        'system_id': frn[3],
        'component': frn[4],
        'source': frn[5],
        'resource_type': frn[6],
        'prefix_path': frn[7],
        'sub_path': frn[8]
    }


def merge_frn(parent_frn_info, frn_info):
    """ Merges parent's frn_info with the existing frn_info """
    def get_frn_value(value, parent_value):
        return parent_value if value == '' or value == None else value

    return {
        'namespace': get_frn_value(frn_info.get('namespace'), parent_frn_info.get('namespace')),
        'system_type': get_frn_value(frn_info.get('system_type'), parent_frn_info.get('system_type')),
        'system_id': get_frn_value(frn_info.get('system_id'), parent_frn_info.get('system_id')),
        'component': get_frn_value(frn_info.get('component'), parent_frn_info.get('component')),
        'source': get_frn_value(frn_info.get('source'), parent_frn_info.get('source')),
        'resource_type': frn_info.get('resource_type'),
        'prefix_path': frn_info.get('prefix_path'),
        'sub_path': frn_info.get('sub_path')
    }