#!/usr/bin/env python3

#
# Tests for the ingest module
#

import unittest

from . import ingest


def _parse_contents(contents):
    """ Helper function to parse contents into input blocks """
    input_blocks = list()
    for (path, frn_info) in contents:
        input_blocks.append(
            ingest.build_input_pipeline(path, frn_info)
        )

    return input_blocks


class IngestTest(unittest.TestCase):
    """ Unit tests for Ingest module """
    def test_building_textfile_input_pipeline(self):
        """ Check if the input pipleine is built for single input """
        contents = [
            ('', {'resource_type': 'textfile', 'source': 'apigateway'})
        ]

        input_blocks = _parse_contents(contents)

        blocks = input_blocks[0]

        self.assertEqual(1, len(input_blocks))
        self.assertEqual(2, len(blocks))
        self.assertEqual('apigateway', blocks[0]['cfg']['src'])
        self.assertRegex(blocks[0]['out'], r'apigateway_None_[\d.]+_parse')
        self.assertEqual(blocks[0]['out'], blocks[1]['id'])

    def test_building_multiple_textfile_input_pipeline(self):
        """ Check if the input pipleine is built for multiple inputs """
        contents = [
            ('', {'resource_type': 'textfile', 'source': 'apigateway'}),
            ('', {'resource_type': 'textfile', 'source': 'storage_agent'})
        ]

        input_blocks = _parse_contents(contents)

        self.assertEqual(2, len(input_blocks))
        self.assertEqual('apigateway', input_blocks[0][0]['cfg']['src'])
        self.assertEqual('storage_agent', input_blocks[1][0]['cfg']['src'])

    def test_building_funos_input_pipeline(self):
        """ Check if the input pipleine is built for funos source """
        contents = [
            ('', {'system_type': 'fs1600', 'resource_type': 'textfile', 'source': 'funos'})
        ]

        input_blocks = _parse_contents(contents)

        blocks = input_blocks[0]

        self.assertEqual(1, len(input_blocks))
        self.assertEqual(2, len(blocks))
        self.assertEqual('funos', blocks[0]['cfg']['src'])
        self.assertEqual('FunOSInput', blocks[1]['block'])

    def test_building_controller_input_pipeline(self):
        """ Check if the input pipleine is built for controller services source """
        contents = [
            ('', {'resource_type': 'textfile', 'source': 'apigateway'}),
            ('', {'resource_type': 'textfile', 'source': 'sns'}),
            ('', {'resource_type': 'textfile', 'source': 'dataplacement'}),
        ]

        input_blocks = _parse_contents(contents)

        self.assertEqual(3, len(input_blocks))
        self.assertEqual('apigateway', input_blocks[0][0]['cfg']['src'])
        self.assertEqual('GenericInput', input_blocks[0][1]['block'])
        self.assertEqual('sns', input_blocks[1][0]['cfg']['src'])
        self.assertEqual('KeyValueInput', input_blocks[1][1]['block'])
        self.assertEqual('dataplacement', input_blocks[2][0]['cfg']['src'])
        self.assertIn('pattern', input_blocks[2][0]['cfg'])

    def test_building_storage_agent_input_pipeline(self):
        """ Check if the input pipleine is built for storage_agent source """
        contents = [
            ('', {'resource_type': 'textfile', 'source': 'storage_agent'})
        ]

        input_blocks = _parse_contents(contents)

        blocks = input_blocks[0]
        self.assertEqual(1, len(input_blocks))
        self.assertEqual(2, len(blocks))
        self.assertEqual('storage_agent', blocks[0]['cfg']['src'])
        self.assertIn('pattern', blocks[0]['cfg'])
        self.assertEqual('GenericInput', blocks[1]['block'])

    def test_can_parse_cfg_from_frn(self):
        """ Check if the cfg is being parsed from the FRN """
        contents = [
            ('', {'resource_type': 'textfile', 'source': 'storage_agent', 'system_type': 'host', 'system_id': 'cab22-qa-01'})
        ]

        input_blocks = _parse_contents(contents)
        blocks = input_blocks[0]

        self.assertIn('system_type', blocks[0]['cfg'])
        self.assertIn('system_id', blocks[0]['cfg'])
        self.assertEqual('host', blocks[0]['cfg']['system_type'])
        self.assertEqual('cab22-qa-01', blocks[0]['cfg']['system_id'])