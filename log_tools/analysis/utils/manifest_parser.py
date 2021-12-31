#!/usr/bin/env python3

#
# Parses Manifest file.
#

import logging
import os
import re
import yaml

MANIFEST_FILE_NAME = 'FUNLOG_MANIFEST'


def parse(dir):
    """ Parse the manifest file inside the given directory """
    manifest = dict()
    try:
        manifest_path = os.path.join(dir, MANIFEST_FILE_NAME)
        logging.info(f'Parsing manifest file at {manifest_path}')
        with open(manifest_path) as manifest_file:
            # Replacing tab indentation with spaces since YAML does not
            # support tab indentation.
            manifest = yaml.safe_load(manifest_file.read().replace('\t', ' '))
        manifest = _format_manifest(manifest)
    except yaml.YAMLError as e:
        logging.exception('Could not parse the manifest file.')
    except FileNotFoundError as e:
        logging.warning('Could not find the manifest file.')
    return manifest


def has_manifest(dir):
    """ Returns True if manifest file exists in the given directory """
    manifest_path = os.path.join(dir, MANIFEST_FILE_NAME)
    return os.path.exists(manifest_path)


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
    frn_pattern = r'(?:\"(.*?)\"(?::|\Z)|(.*?)(?::|\Z))'
    frn_match = re.findall(frn_pattern, frn_str)

    def get_frn_component(index):
        frn = frn_match[index]
        return frn[0] if frn[0] and frn[0] != '' else frn[1]

    return {
        'namespace': get_frn_component(1),
        'system_type': get_frn_component(2),
        'system_id': get_frn_component(3),
        'component': get_frn_component(4),
        'source': get_frn_component(5),
        'resource_type': get_frn_component(6),
        'prefix_path': get_frn_component(7),
        # TODO(Sourabh): Need to enusure all the values are enclosed
        # with quotes so to avoid this issue. Left the fallback for
        # now.
        #
        # The file names of some log archives are of the format:
        # cs-logs-2021-04-28-11:25:20.tgz
        'sub_path': get_frn_component(8)
                    # Regex finds 10 matches for the frn string
                    if len(frn_match) == 10
                    else ':'.join([get_frn_component(index)
                                    for index in range(8, len(frn_match)-1)])
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