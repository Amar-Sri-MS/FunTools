#!/usr/bin/env python3

#
# Parses Manifest file.
#

import os
import sys
import yaml

MANIFEST_FILE_NAME = 'FUNLOG_MANIFEST'


def parse(dir):
    """ Parse the manifest file inside the given directory """
    manifest = dict()
    try:
        manifest_path = os.path.join(dir, MANIFEST_FILE_NAME)
        print('Parsing manifest file at', manifest_path)
        with open(manifest_path) as manifest_file:
            manifest = yaml.safe_load(manifest_file)
        manifest = _format_manifest(manifest)
    except yaml.YAMLError as e:
        print('Could not parse the manifest file. Error:', e)
    except FileNotFoundError as e:
        print('Could not find the manifest file.')
    return manifest


def _format_manifest(manifest):
    contents = list()
    for content in manifest['contents']:
        if type(content) == str:
            contents.append(content)

        # In case the last element of the FRN is empty, pyyaml
        # considers it a dict since the last character is :
        if type(content) == dict:
            frn = content.keys()[0]
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