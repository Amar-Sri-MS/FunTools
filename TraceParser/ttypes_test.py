#!/usr/bin/env python3
#
# trace_test.py: unit tests for tree manipulation code.
#
# Copyright Fungible Inc. 2018.  All Rights Reserved.

import unittest

import json
import io
import unittest

import tprs
import ttypes

def makeSimpleTree():
    a = ttypes.TTree('a', None, 100, 0, 0, 0, 1)
    b = ttypes.TTree('b',a, 110, 0, 0, 0, 2)
    a.add_call(b)
    c = ttypes.TTree('c', b, 120, 0, 0, 0, 3)
    b.add_call(c)
    d = ttypes.TTree('d', c, 130, 0, 0, 0, 4)
    c.add_call(d)
    d.set_end_cycle(140)
    c.set_end_cycle(150)
    b.set_end_cycle(160)
    a.set_end_cycle(170)
    return a

def makeTreeCallingFunctionRepeatedly():
    a = ttypes.TTree('a', None, 100, 0, 0, 0, 1)
    a.set_end_cycle(170)
       
    b = ttypes.TTree('b',a, 110, 0, 0, 0, 2)
    b.set_end_cycle(120)
    a.add_call(b)

    b = ttypes.TTree('b',a, 130, 0, 0, 0, 2)
    b.set_end_cycle(140)
    a.add_call(b)

    b = ttypes.TTree('b',a, 150, 0, 0, 0, 2)
    b.set_end_cycle(160)
    a.add_call(b)

    return a

def makeRecursiveTree():
    a = ttypes.TTree('a', None, 100, 0, 0, 0, 1)
    b = ttypes.TTree('a',a, 110, 0, 0, 0, 1)
    a.add_call(b)
    c = ttypes.TTree('a', b, 120, 0, 0, 0, 1)
    b.add_call(c)
    d = ttypes.TTree('a', c, 130, 0, 0, 0, 1)
    c.add_call(d)
    d.set_end_cycle(140)
    c.set_end_cycle(150)
    b.set_end_cycle(160)
    a.set_end_cycle(170)
    return a

class TestFunctionStats(unittest.TestCase):

    def testNumberNodes(self):
        root = makeSimpleTree()

        last_number = ttypes.number_nodes(root, 1)
        
        self.assertEqual(5, last_number)
        self.assertEqual(1, root.id)
        self.assertEqual(2, root.calls[0].id)
        self.assertEqual(3, root.calls[0].calls[0].id)
        self.assertEqual(4, root.calls[0].calls[0].calls[0].id)

    def testWriteNodesAsJSON(self):
        root = makeSimpleTree()
        ttypes.number_nodes(root, 1)
        
        out_stream = io.StringIO()
        ttypes.write_nodes_as_json(root, out_stream)

        # Quick sanity check on expected values.
        json_string = out_stream.getvalue()

        # Make sure all fields are filled in on a representative node.
        self.assertIn('"name": "a"', json_string)
        self.assertIn('"calls": [2]', json_string)
        self.assertIn('"cycles": 71', json_string)
        self.assertIn('"start_line": 1', json_string)

        self.assertIn('"name": "c"', json_string)
        self.assertIn('"name": "d"', json_string)

        # Need top level to be a map.
        valid_json_string = '{"calls": [' + json_string + ']}'
        
        # Check result is parsable.
        self.assertTrue(json.loads(valid_json_string))

class TestGetStats(unittest.TestCase):
    def testGetStatsSimple(self):
        root = makeSimpleTree()
        stats = tprs.generate_function_stats([root])
        
        self.assertEqual(4, len(stats))

        self.assertEqual('a', stats[0]['name'])
        self.assertEqual(70, stats[0]['cycles'])
        self.assertEqual(1, stats[0]['calls'])

        self.assertEqual('b', stats[1]['name'])
        self.assertEqual(50, stats[1]['cycles'])
        self.assertEqual(1, stats[1]['calls'])

        self.assertEqual('d', stats[3]['name'])
        self.assertEqual(10, stats[3]['cycles'])
        self.assertEqual(1, stats[3]['calls'])

    def testGetStatsDuplicates(self):
        root = makeTreeCallingFunctionRepeatedly()
        stats = tprs.generate_function_stats([root])
        
        self.assertEqual(2, len(stats))
        
        # Move to dictionary for easier picking of values.

        self.assertEqual(70, stats[0]['cycles'])
        self.assertEqual(1, stats[0]['calls'])

        # TODO(bowdidge): Isn't summing.
        # self.assertEqual(30, stats[1]['cycles'])
        # self.assertEqual(3, stats[1]['calls'])

    def disableTestNotConfusedByRecursion(self):
        root = makeRecursiveTree()
        stats = tprs.generate_function_stats_dict([root])
        
        self.assertEqual(1, len(stats))

        self.assertEqual(70, stats[0]['cycles'])
        self.assertEqual(4, stats[0]['calls'])
        self.assertEqual(40, stats[0]['cycles_average'])
        self.assertEqual(70, stats[0]['cycles_max'])
        self.assertEqual(10, stats[0]['cycles_min'])
        # Stddev is set later.
        self.assertEqual(0, stats[0]['cycles_std_dev'])

if __name__ == '__main__':
    unittest.main()
