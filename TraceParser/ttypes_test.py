#
# trace_test.py: unit tests for tree manipulation code.
#
# Copyright Fungible Inc. 2018.  All Rights Reserved.

import json
import StringIO
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
    a.add_call(b)
    b.set_end_cycle(120)

    b = ttypes.TTree('b',a, 130, 0, 0, 0, 2)
    a.add_call(b)
    b.set_end_cycle(140)

    b = ttypes.TTree('b',a, 150, 0, 0, 0, 2)
    a.add_call(b)
    b.set_end_cycle(160)

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
        
        out_stream = StringIO.StringIO()
        ttypes.write_nodes_as_json(root, out_stream)

        # Quick sanity check on expected values.
        json_string = out_stream.getvalue()

        # Make sure all fields are filled in on a representative node.
        self.assertIn('"name": "a"', out_stream.getvalue())
        self.assertIn('"calls": [3]', out_stream.getvalue())
        self.assertIn('"start_cycle": 100', out_stream.getvalue())
        self.assertIn('"end_cycle": 170', out_stream.getvalue())
        self.assertIn('"start_line": 4', out_stream.getvalue())

        self.assertIn('"name": "a"', out_stream.getvalue())
        self.assertIn('"name": "d"', out_stream.getvalue())

        # Need top level to be a map.
        valid_json_string = '{"calls": [' + json_string + ']}'
        
        # Check result is parsable.
        self.assertTrue(json.loads(valid_json_string))

class TestGetStats(unittest.TestCase):
    def testGetStatsSimple(self):
        root = makeSimpleTree()
        stats_dict = tprs.generate_function_stats_dict([root])
        
        self.assertEqual(4, len(stats_dict))

        self.assertEqual(70, stats_dict['a']['cycles'])
        self.assertEqual(1, stats_dict['a']['calls'])

        self.assertEqual(50, stats_dict['b']['cycles'])
        self.assertEqual(1, stats_dict['b']['calls'])

        self.assertEqual(10, stats_dict['d']['cycles'])
        self.assertEqual(1, stats_dict['d']['calls'])

    def testGetStatsDuplicates(self):
        root = makeTreeCallingFunctionRepeatedly()
        stats_dict = tprs.generate_function_stats_dict([root])
        
        self.assertEqual(2, len(stats_dict))

        self.assertEqual(70, stats_dict['a']['cycles'])
        self.assertEqual(1, stats_dict['a']['calls'])

        self.assertEqual(30, stats_dict['b']['cycles'])
        self.assertEqual(3, stats_dict['b']['calls'])

    def testNotConfusedByRecursion(self):
        root = makeRecursiveTree()
        stats_dict = tprs.generate_function_stats_dict([root])
        
        self.assertEqual(1, len(stats_dict))

        # Total cycles is a little misleading here because we're double-counting
        # the recursive calls.
        self.assertEqual(160, stats_dict['a']['cycles'])
        self.assertEqual(4, stats_dict['a']['calls'])
        self.assertEquals(40, stats_dict['a']['cycles_average'])
        self.assertEquals(70, stats_dict['a']['cycles_max'])
        self.assertEquals(10, stats_dict['a']['cycles_min'])
        # Stddev is set later.
        self.assertEquals(0, stats_dict['a']['cycles_std_dev'])

if __name__ == '__main__':
    unittest.main()
