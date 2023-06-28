#!/usr/bin/env python3

#
# Checker for log stress test app in FunOS
#

import argparse
import re


class VpLogChecker:
    """Per-VP log checker"""

    # Message emitted by test app
    msg_re = re.compile(r'.*"Sequence: (\d+) Len: (\d+) (\w*)"')

    def __init__(self, vpnum):
        self.vpnum = vpnum
        # expected message counter
        self.counter = 0
        # every two elements marks [start, end_exclusive) range
        self.missing_ranges = []
        # drop state
        self.in_drop = False
        # verbose
        self.verbose = False

    def check(self, timestamp, msg):
        """Check the message"""
        m = self.msg_re.match(msg)
        if m:
            seq = int(m.group(1))
            length = int(m.group(2))
            test_str = m.group(3)

            if self._check_seq(seq):
                # only check the string if the sequence matches
                # to reduce verbosity on failure
                self._check_test_str(timestamp, test_str, length)

            self.counter = seq + 1
        else:
            # assume this is just a normal log from FunOS
            pass

    def _check_seq(self, seq):
        if seq != self.counter:
            # TODO correlate to drop message
            if not self.in_drop:
                self.missing_ranges.append(seq)
            self.in_drop = True
        else:
            if self.in_drop:
                self.missing_ranges.append(seq)
            self.in_drop = False

        return seq == self.counter

    def _check_test_str(self, timestamp, test_str, length):
        actual = len(test_str)
        if actual != length:
            print(
                "[%s] VP %d expected length %d got %d"
                % (timestamp, self.vpnum, length, actual)
            )

        exp_letter = chr(ord("a") + (self.counter & 0xF))
        exp_str = exp_letter * length
        if exp_str != test_str:
            print(
                "[%s] VP %d expected string %s got %s"
                % (timestamp, self.vpnum, exp_str, test_str)
            )

    def missing_range_summary(self):
        """Return a summary of missing ranges"""
        r = ""
        if self.missing_ranges:
            r += "VP %d missing ranges: " % self.vpnum
            r += str(self.missing_ranges)
            r += "\n"
        return r


class GlobalLogChecker:
    # Constants
    MAX_CLUSTERS = 9
    VPS_PER_CLUSTER = 24
    VPS_PER_CORE = 4

    # FunOS log line prefix with timestamp and VP
    msg_re = re.compile(r"\[([\d.]+) ([\d.]+)\](.*)")

    def __init__(self):
        self.vp_checkers = []
        self._init_vp_checkers()
        self.last_secs = -1
        self.last_nsecs = -1

    def _init_vp_checkers(self):
        for i in range(0, self.MAX_CLUSTERS * self.VPS_PER_CLUSTER):
            self.vp_checkers.append(VpLogChecker(i))

    def _vp_from_ccv(self, ccv):
        cluster, core, vpl = ccv.split(".")
        return (
            int(cluster) * self.VPS_PER_CLUSTER
            + int(core) * self.VPS_PER_CORE
            + int(vpl)
        )

    def check(self, msg):
        """Check the message"""
        m = self.msg_re.match(msg)
        if m:
            timestamp = m.group(1)
            self._check_ordering(timestamp)

            vp = self._vp_from_ccv(m.group(2))
            self.vp_checkers[vp].check(timestamp, m.group(3))

    def _check_ordering(self, timestamp):
        parts = timestamp.split(".")
        secs = int(parts[0])
        nsecs = int(parts[1])

        reverse = False
        if secs < self.last_secs:
            reverse = True
        elif secs == self.last_secs and nsecs < self.last_nsecs:
            reverse = True

        if reverse:
            print(
                "[%s] Message precedes prior message at [%d.%d]"
                % (timestamp, self.last_secs, self.last_nsecs)
            )
        else:
            self.last_secs = secs
            self.last_nsecs = nsecs

    def status(self):
        r = "Global checker status\n"
        r += "---------------------\n"
        for c in self.vp_checkers:
            missing = c.missing_range_summary()
            if missing:
                r += missing
        return r


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="log file")
    args = parser.parse_args()

    checker = GlobalLogChecker()
    fh = open(args.filename, "r")

    for line in fh:
        checker.check(line)

    print(checker.status())


if __name__ == "__main__":
    main()
