#!/usr/bin/env python3

#
# Tests for parsing FUNLOG_MANIFEST
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import unittest

import manifest_parser


class ManifestParserTest(unittest.TestCase):
    """ Unite tests for parsing FUNLOG_MANIFEST """
    def test_parse_frn(self):
        """ Check to parse a simple frn string """
        frn_str = 'frn:platform:DPU::host:funos:textfile::odp/uartout0.0.txt'
        frn = {
            'namespace': 'platform',
            'system_type': 'DPU',
            'system_id': None,
            'component': 'host',
            'source': 'funos',
            'resource_type': 'textfile',
            'prefix_path': None,
            'sub_path': 'odp/uartout0.0.txt'
        }

        parsed_frn = manifest_parser.parse_FRN(frn_str)
        self.assertDictEqual(frn, parsed_frn)

    def test_parse_frn_with_special_characters_within_quotes(self):
        """ Check to parse an frn string with special characters """
        frn_str = 'frn:platform:DPU:"demand-telemetry-01.fungible.local:11000:f1_0":host:funos:textfile::odp/uartout0.0.txt'
        frn = {
            'namespace': 'platform',
            'system_type': 'DPU',
            'system_id': 'demand-telemetry-01.fungible.local:11000:f1_0',
            'component': 'host',
            'source': 'funos',
            'resource_type': 'textfile',
            'prefix_path': None,
            'sub_path': 'odp/uartout0.0.txt'
        }

        parsed_frn = manifest_parser.parse_FRN(frn_str)
        self.assertDictEqual(frn, parsed_frn)

    def test_parse_frn_with_special_characters_in_subpath_without_quotes(self):
        """ Check to parse an frn string with special characters in subpath without quotes """
        frn_str = 'frn:platform:DPU::host:funos:textfile::cs-logs-2021-04-28-11:25:20.tgz'
        frn = {
            'namespace': 'platform',
            'system_type': 'DPU',
            'system_id': None,
            'component': 'host',
            'source': 'funos',
            'resource_type': 'textfile',
            'prefix_path': None,
            'sub_path': 'cs-logs-2021-04-28-11:25:20.tgz'
        }

        parsed_frn = manifest_parser.parse_FRN(frn_str)
        self.assertDictEqual(frn, parsed_frn)

    def test_merge_frn(self):
        """ Check to merge two frn """
        frn_1 = {
            'namespace': 'platform',
            'system_type': 'DPU',
            'system_id': None,
            'component': 'host',
            'source': 'funos',
            'resource_type': 'textfile',
            'prefix_path': None,
            'sub_path': 'odp/uartout0.0.txt'
        }

        frn_2 = {
            'system_id': 'demand-telemetry-01.fungible.local:11000:f1_0',
            'resource_type': 'textfile',
            'prefix_path': 'odp',
            'sub_path': 'uartout0.0.txt'
        }

        frn = {
            'namespace': 'platform',
            'system_type': 'DPU',
            'system_id': 'demand-telemetry-01.fungible.local:11000:f1_0',
            'component': 'host',
            'source': 'funos',
            'resource_type': 'textfile',
            'prefix_path': 'odp',
            'sub_path': 'uartout0.0.txt'
        }

        merged_frn = manifest_parser.merge_frn(frn_1, frn_2)
        self.assertDictEqual(frn, merged_frn)

    def test_duplicate_frn_entries(self):
        """ Check if the manifest contents does not have duplicate FRN entries """
        manifest = {
            'contents': [
                'frn:platform:DPU::host:funos:textfile::cs-logs-2021-04-28-11:25:20.tgz',
                'frn:platform:DPU::host:funos:textfile::cs-logs-2021-04-28-11:25:20.tgz'
            ]
        }

        expected_manifest = {
            'contents': [
                'frn:platform:DPU::host:funos:textfile::cs-logs-2021-04-28-11:25:20.tgz'
            ]
        }

        formatted_manifest = manifest_parser._format_manifest(manifest)
        self.assertDictEqual(expected_manifest, formatted_manifest)