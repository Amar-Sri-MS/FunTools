#!/usr/bin/env python3

#
# Tests for the pipeline module.
#

import unittest

import pipeline

from blocks.block import Block


class Producer(Block):
    """ Produces a single value (its id) """
    def __init__(self):
        self.id = None

    def process(self, iters):
        yield self.id

    def set_config(self, config):
        self.id = config['uid']


class Consumer(Block):
    """ Stores all incoming values for later inspection """
    def __init__(self):
        self.id = None
        self.vals = []

    def process(self, iters):
        for iter in iters:
            for val in iter:
                self.vals.append(val)

    def set_config(self, config):
        self.id = config['uid']


class PassthroughBlock(Block):
    """ Pass-through mock. """
    def __init__(self):
        self.seen = []
        self.id = None

    def process(self, iters):
        for iter in iters:
            for val in iter:
                self.seen.append(val)
                yield val

    def set_config(self, config):
        self.id = config['uid']


class MockBlockFactory(object):
    """ Block factory for tests """

    def __init__(self):
        self.blocks = []

    def create_block(self, block_name):
        if block_name == 'Producer':
            block = Producer()
        elif block_name == 'Consumer':
            block = Consumer()
        else:
            block = PassthroughBlock()
        self.blocks.append(block)
        return block

    def get_block(self, id):
        """ Obtains the block by its id or None if it isn't there """
        for block in self.blocks:
            if block.id == id:
                return block


class PipelineTest(unittest.TestCase):
    """
    General note: in these test cases we cheat by passing strings around
    instead of the standard tuple. This is fine because the pipeline
    module is agnostic about the data format.
    """
    def setUp(self):
        self.factory = MockBlockFactory()

    def test_can_connect_output_to_input(self):
        """ Basic check: connect two blocks and have data move through them """
        cfg = {}
        cfg['pipeline'] = [
            {
                'id': 'uno',
                'block': 'Producer',
                'out': 'dos'
            },
            {
                'id': 'dos',
                'block': 'Consumer'
            }
        ]

        pipe = pipeline.Pipeline(self.factory, cfg, {})
        pipe.process()

        consumer = self.factory.get_block('dos')

        vals = consumer.vals
        self.assertEqual(1, len(vals))
        self.assertEqual('uno', vals[0])

    def test_multiple_inputs_to_one_block(self):
        cfg = {}
        cfg['pipeline'] = [
            {
                'id': 'humpty',
                'block': 'Producer',
                'out': 'cons'
            },
            {
                'id': 'dumpty',
                'block': 'Producer',
                'out': 'cons'
            },
            {
                'id': 'cons',
                'block': 'Consumer'
            }
        ]

        pipe = pipeline.Pipeline(self.factory, cfg, {})
        pipe.process()

        consumer = self.factory.get_block('cons')

        vals = consumer.vals
        self.assertEqual(2, len(vals))
        self.assertIn('humpty', vals)
        self.assertIn('dumpty', vals)

    def test_correct_ordering_of_pipeline_blocks(self):
        """ Ensures the pipeline blocks are ordered correctly """

        # Declare the pipeline in scrambled order
        cfg = {}
        cfg['pipeline'] = [
            {
                'id': 'cons',
                'block': 'Consumer'
            },
            {
                'id': 'pony_pass',
                'block': 'Passthrough',
                'out': 'cons'
            },
            {
                'id': 'pony',
                'block': 'Producer',
                'out': 'pony_pass'
            },
            {
                'id': 'my',
                'block': 'Producer',
                'out': 'cons'
            },
            {
                'id': 'little',
                'block': 'Producer',
                'out': 'little_pass'
            },
            {
                'id': 'little_pass',
                'block': 'Passthrough',
                'out': 'cons'
            }
        ]

        pipe = pipeline.Pipeline(self.factory, cfg, {})
        pipe.process()

        consumer = self.factory.get_block('cons')

        vals = consumer.vals
        self.assertIn('my', vals)
        self.assertIn('little', vals)
        self.assertIn('pony', vals)
