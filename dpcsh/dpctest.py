#!/usr/bin/env python2.7
##
##  dpc_test.py
##
##  Created by Charles Gray on 2018-03-19
##  Copyright (C) 2018 Fungible. All rights reserved.
##

import json
import os
import sys
import subprocess
import dpc_client
import time
import unittest


class TestDPCCommands(unittest.TestCase):
    """Tests that standard DPC commands.
    """

    def __init__(self, client, method):
        self.client = client
        self._testMethodName = method
        testMethod = getattr(self, method)
        self._testMethodDoc = testMethod.__doc__
        self._cleanups = []

        # Map types to custom assertEqual functions that will compare
        # instances of said type in more detail to generate a more useful
        # error message.
        self._type_equality_funcs = {}
        self.addTypeEqualityFunc(dict, self.assertDictEqual)
        self.addTypeEqualityFunc(list, self.assertListEqual)
        self.addTypeEqualityFunc(tuple, self.assertTupleEqual)
        self.addTypeEqualityFunc(set, self.assertSetEqual)
        self.addTypeEqualityFunc(frozenset, self.assertSetEqual)
        self.addTypeEqualityFunc(unicode, self.assertMultiLineEqual)

    def testEcho(self):
        """Tests the echo command returns the string passed in."""
        label = 'foo'
        ret = self.client.execute('echo', [label])
        print 'dpc.execute returned %s' % ret
        self.assertEquals(label, ret)

    def checkEchoMessage(self, message):
        result = self.client.execute('echo', [message])
        self.assertIsNotNone(result)
        self.assertEquals(message, result.strip())

    def testSeveralEcho(self):
        """Tests the echo command returns the string passed in."""
        for i in range(0, 10):
            self.checkEchoMessage('foo %d' % i)

    def testMath(self):
        ret = self.client.execute('math', ['+', 2, 3, 4, 5, 6])
        self.assertIsNotNone(ret)
        self.assertEquals(20, int(ret))

    def testApp(self):
        ret = self.client.execute('debug', ['fibo', 10])
        print 'testApp returned %s' % ret

    def testLargeCommands(self):
        """Tests that long messages don't get truncated or corrupted."""
        for i in (10, 100, 1000):
            print 'Attempting message of length %d' % i
            self.checkEchoMessage('a' * i)

    def testVeryLargeCommands(self):
        """Tests that long messages don't get truncated or corrupted."""
        for i in (10000, 100000):
            print 'Attempting message of length %d' % i
            self.checkEchoMessage('b' * i)

    def testAsync(self):
        """Test asynchronous events return in expected order."""
        self.client.async_send("delay", [3, "echo", "third"])
        self.client.async_send("delay", [2, "echo", "second"])
        self.client.async_send("delay", [1, "echo", "first"])

        r1 = self.client.async_recv_any()
        r2 = self.client.async_recv_any()
        r3 = self.client.async_recv_any()

        self.assertEqual('first', r1)
        self.assertEqual('second', r2)
        self.assertEqual('third', r3)

    def testJumbo(self):
        """ Testing jumbo async"""
        jumbo_message = "a" * 100000
        self.client.async_send("echo", jumbo_message)
        self.client.async_send("echo", jumbo_message)
        self.client.async_send("echo", jumbo_message)
        r1 = self.client.async_recv_any()
        r2 = self.client.async_recv_any()
        r3 = self.client.async_recv_any()

        self.assertEqual(r2, r1)
        self.assertEqual(r3, r1)


def run_tests_client(client, exclude):
    suite = unittest.TestSuite()
    for func in dir(TestDPCCommands):
        if callable(getattr(TestDPCCommands, func)) and func.startswith('test') \
            and (func not in exclude):
            suite.addTest(TestDPCCommands(client, func))
    unittest.TextTestRunner().run(suite)

def run_dpc_test(args, legacy_ok, delay):
    """ Load up a dpcsh tcp socket """
    print "### Running dpcsh as text proxy"
    pid = subprocess.Popen(["./dpcsh", "--oneshot"] + args)

    print "### pid is %s" % pid
    time.sleep(1)

    # connect to it
    client = dpc_client.DpcClient(False, legacy_ok)

    time.sleep(delay)
    run_tests_client(client, [])


def run_using_env(exclude):
    """ Initializes DPC client from env.json, runs standard tests """
    f = open('./env.json', 'r')
    env_dict = json.load(f)
    
    if len(env_dict['dpc_hosts']) != 1:
        raise RuntimeError("configuration error")

    dpc_host = env_dict['dpc_hosts'][0]
    host = dpc_host['host']
    port = dpc_host['tcp_port']
    print 'Connecting to dpc host at %s:%s' % (host, port)
    client = dpc_client.DpcClient(server_address=(host, port))

    run_tests_client(client, exclude)


STYLES = {"tcp": (True, ["--verbose", "--tcp_proxy"], False, 0),
          "unix": (True, ["--verbose", "--unix_proxy"], True, 0),
          "qemu": (False, ["--verbose", "--tcp_proxy", "--base64_sock"], False, 10)}


def run_style(manual, style):

    (auto, args, legacy_ok, delay) = STYLES[style]

    if (manual or auto):
        print "Running tests for '%s'" % style
        run_dpc_test(args, legacy_ok, delay)
    else:
        print "Skipping '%s'" % style


def usage():
    print "usage: %s [tcp, unix, qemu, fun-on-demand, fun-on-demand-reduced]" % sys.argv[0]
    sys.exit(1)


def main():

    if (len(sys.argv) > 2):
        usage()

    style = None
    if (len(sys.argv) == 2):
        style = sys.argv[1]

    if style == 'fun-on-demand' or style == 'fun-on-demand-reduced':
        exclude = ['testVeryLargeCommands', 'testAsync', 'testJumbo'] \
            if style == 'fun-on-demand-reduced' else []
        run_using_env(exclude)
        return

    if (style is not None):
        run_style(True, style)
    else:
        for style in STYLES:
            run_style(False, style)


###
##  entrypoint
#
if (__name__ == "__main__"):
    main()
