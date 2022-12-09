#!/usr/bin/env python3
##
##  dpc_test.py
##
##  Created by Charles Gray on 2018-03-19
##  Copyright (C) 2018 Fungible. All rights reserved.
##

from __future__ import print_function
import json
import sys
import socket
import subprocess
import tempfile
import dpc_client
import time
import unittest
import xmlrunner
import dpc_binary

class TestDPCCommands(unittest.TestCase):
    """Tests that standard DPC commands.
    """

    # TODO(bowdidge): Don't use non-standard init because it breaks standard
    # unit test framework calls.
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
        self.addTypeEqualityFunc(str, self.assertMultiLineEqual)

    def testEcho(self):
        """Tests the echo command returns the string passed in."""
        label = 'foo'
        ret = self.client.execute('echo', [label])
        print('dpc.execute returned %s' % ret)
        self.assertEqual(label, ret)

    def checkEchoMessage(self, message):
        result = self.client.execute('echo', [message])
        self.assertIsNotNone(result)
        self.assertEqual(message, result.strip())

    def testSeveralEcho(self):
        """Tests the echo command returns the string passed in."""
        for i in range(0, 10):
            self.checkEchoMessage('foo %d' % i)

    def testMath(self):
        ret = self.client.execute('math', ['+', 2, 3, 4, 5, 6])
        self.assertIsNotNone(ret)
        self.assertEqual(20, int(ret))

    def testApp(self):
        ret = self.client.execute('debug', ['fibo', 10])
        print('testApp returned %s' % ret)

    def testTimeout(self):
        self.client.set_timeout(0.5)
        try:
            self.client.execute('sleep', [2])
            self.assertTrue(False)
        except dpc_client.DpcTimeoutError:
            print('timeout works')
            self.client.set_timeout(None)
            self.client.async_recv_any()

    def testLargeCommands(self):
        """Tests that long messages don't get truncated or corrupted."""
        for i in (10, 100, 1000):
            print('Attempting message of length %d' % i)
            self.checkEchoMessage('a' * i)

    def testVeryLargeCommands(self):
        """Tests that long messages don't get truncated or corrupted."""
        for i in (10000, 50000, 100000, 1000000):
            print('Attempting message of length %d' % i)
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

    def testSubscription(self):
        """ Testing subscriptions """
        ticket = self.client.execute('notification', ['register', 'test_note_1', ''])
        self.assertIsInstance(ticket, int)
        ret = self.client.execute('notification', ['test_emit_periodic'])
        self.assertEqual(ret, u'timer will post \'test_note_1\' every second')
        for _ in range(0, 3):
            ret = self.client.async_recv_wait(0, True, 2)
            self.assertEqual(ret['cookie'], '')
            self.assertEqual(ret['note'], 'test_note_1')
        ret = self.client.execute('notification', ['unregister', 'test_note_1', ticket])
        self.assertEqual(ret, True)
        ret = self.client.execute('notification', ['test_emit_periodic'])
        self.assertEqual(ret, u'timer stopped')


    def testBlob(self):
        with tempfile.NamedTemporaryFile() as fp:
            original_data = b'b' * 100000
            fp.write(original_data)
            fp.flush()
            uuid = self.client.execute('blob', ['store', self.client.dpc_blob_from_file(fp.name)])
            data = self.client.blob_to_string(self.client.execute('blob', ['retrieve', uuid]))
            self.assertEqual(original_data, data)


def run_tests_client(client, exclude):
    """Run the unit tests with extra args for global client and exclude list.

    Returns True if all tests passed.
    """
    suite = unittest.TestSuite()
    for func in dir(TestDPCCommands):
        if callable(getattr(TestDPCCommands, func)) and func.startswith('test') \
            and (func not in exclude):
            suite.addTest(TestDPCCommands(client, func))
    test_runner = xmlrunner.XMLTestRunner(output="logs/")
    results = test_runner.run(suite)
    return len(results.failures) == 0

def run_dpc_test(args, unix_sock, delay):
    """ Load up a dpcsh tcp socket """
    print("### Running dpcsh as text proxy")
    pid = subprocess.Popen(["./dpcsh", "--oneshot"] + args)

    print("### pid is %s" % pid)
    time.sleep(1)

    try:
        # connect to it
        client = dpc_client.DpcClient(legacy_ok = False, unix_sock = unix_sock)

        time.sleep(delay)
        return run_tests_client(client, [])
    finally:
        if pid.returncode is None:
            pid.terminate()


def get_dpc_host_and_port(style):
    f = open('./env.json', 'r')
    env_dict = json.load(f)

    # TODO(ridrisov): remove separate check once fun-on-demand support DPC proxy on CC Linux
    if style == 'fun-on-demand-cc':
        if len(env_dict['cclinux_hosts']) != 1:
            raise RuntimeError("configuration error")
        return env_dict['cclinux_hosts'][0]['host'], 4223

    if len(env_dict['dpc_hosts']) != 1:
        raise RuntimeError("configuration error")

    dpc_host = env_dict['dpc_hosts'][0]
    return dpc_host['host'], dpc_host['tcp_port']


def wait_for_port(host, port, timeout):
    start_time = time.time()
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, int(port)))
            break
        except:
            time.sleep(0.5)
            if time.time() - start_time >= timeout:
                raise Exception('Timeout while waiting for the port to open')


def run_using_env(style, exclude):
    """ Initializes DPC client from env.json, runs standard tests """

    host, port = get_dpc_host_and_port(style)
    wait_for_port(host, port, 60)

    print('Connecting to dpc host at %s:%s' % (host, port))
    client = dpc_client.DpcClient(server_address=(host, port))

    if not run_tests_client(client, exclude):
        return False

    print('Checking the same with binary protocol')
    binary_client = dpc_client.DpcClient(server_address=(host, port), encoder=dpc_binary.BinaryJSONEncoder())

    return run_tests_client(binary_client, exclude)


STYLES = {"tcp": (True, ["--verbose", "--tcp_proxy"], False, 0),
          "unix": (True, ["--verbose", "--unix_proxy"], True, 0),
          "qemu": (False, ["--verbose", "--tcp_proxy", "--base64_sock"], False, 10)}


def run_style(manual, style):

    (auto, args, unix_sock, delay) = STYLES[style]

    if (manual or auto):
        print("Running tests for '%s'" % style)
        return run_dpc_test(args, unix_sock, delay)
    else:
        print("Skipping '%s'" % style)
        # Pretend all tests passed.
        return True


def usage():
    print("usage: %s [tcp, unix, qemu, fun-on-demand, fun-on-demand-cc, fun-on-demand-reduced]" % sys.argv[0])
    sys.exit(1)


def main():

    if (len(sys.argv) > 2):
        usage()

    style = None
    if (len(sys.argv) == 2):
        style = sys.argv[1]

    tests_passed = True

    if style == 'fun-on-demand' or style == 'fun-on-demand-cc' \
        or style == 'fun-on-demand-reduced':
        exclude = ['testVeryLargeCommands', 'testAsync', 'testJumbo'] \
            if style == 'fun-on-demand-reduced' or style == 'fun-on-demand-cc' else []
        tests_passed = run_using_env(style, exclude)

    elif style is not None:
        tests_passed = run_style(True, style)

    else:
        for style in STYLES:
            ret = run_style(False, style)
            if not ret:
                tests_passed = False
                # Keep going just for coverage.

    if not tests_passed:
        sys.exit(1)
    else:
        sys.exit(0)


###
##  entrypoint
#
if (__name__ == "__main__"):
    main()
