#
# Parsers for log lines from various sources
#

import datetime
import io
import math
import os
import re

from blocks.block import Block


class FunOSInput(Block):
    """ Handles FunOS log files """
    def process(self, iters):
        return self.lines2tuples(iters[0])

    def lines2tuples(self, iter):
        uboot_done = False

        for (_, _, uid, _, line) in iter:
            line = line.strip()

            if not uboot_done and self.is_uboot(line):
                # TODO (jimmy): deal with u-boot lines
                continue
            else:
                uboot_done = True

                # Example:
                # [23.855474 1.5.2] NOTICE nvdimm ...
                ts_vp_sep = line.find(']')

                # Empty or malformed line ewwwww
                if ts_vp_sep == -1:
                    continue

                ts_vp = line[1:ts_vp_sep]
                ts, vp = self.split_ts_vp(ts_vp)

                secs, usecs = self.normalize_ts(ts)
                line = '[{}] {}'.format(vp, line[ts_vp_sep + 1:])

                yield (secs, usecs, uid, None, line)

    @staticmethod
    def is_uboot(line):
        """
        Silly heuristic that determines if a line is u-boot or not.

        Only needs to work until the first non u-boot line is detected, after which
        it should not be called.
        """
        if not line.startswith('['):
            return True

        return 'microseconds' in line[:30]

    @staticmethod
    def split_ts_vp(ts_vp):
        ts_vp_parts = ts_vp.split(' ')
        return (ts_vp_parts[0], ts_vp_parts[1])

    @staticmethod
    def normalize_ts(ts):
        """
        Split the timestamp into seconds and microseconds.
        """
        dot_idx = ts.find('.')

        secs = ts[:dot_idx]
        usecs = ts[dot_idx+1:]

        return int(secs), int(usecs)


class ISOFormatInput(Block):
    """ Handles logs with ISO format timestamps """
    def process(self, iters):
        for (_, _, uid, _, line) in iters[0]:
            line = line.strip()

            # Example:
            # 2020-07-09 16:37:59.240281 Start probing thread
            parts = line.split(' ', 2)

            iso_format_datetime = parts[0] + ' ' + parts[1]
            d = datetime.datetime.fromisoformat(iso_format_datetime)

            ts = d.timestamp()
            secs, usecs = self.normalize_ts(ts)

            yield (secs, usecs, uid, None, parts[2])

    @staticmethod
    def normalize_ts(ts):
        useconds, seconds = math.modf(ts)
        return int(seconds), int(useconds * 1e6)


class MsecInput(Block):
    """
    Handles logs with millisecond timestamp granularity as emitted by
    python's default logger (and various go microservices in the controller)
    """
    def process(self, iters):
        for (_, _, uid, _, line) in iters[0]:
            line = line.strip()

            # 2020-08-03 14:13:04,086 INFO XXX
            m = re.match('^([-0-9]+)\s+([:0-9]+),([0-9]+)\s+(.*)', line)

            if not m:
                # 2020/08/05 02:48:10.850 INFO    tracer
                m = re.match('^([/0-9]+)\s+([:0-9]+)\.([0-9]+)\s+(.*)', line)

            if m:
                secs, usecs = self.extract_timestamp(m.group(1), m.group(2),
                                                     m.group(3))
                yield (secs, usecs, uid, None, m.group(4))

    @staticmethod
    def extract_timestamp(day_str, time_str, msecs_str):
        # this approximation could be bad
        usecs_str = str(int(msecs_str) * 1000)

        day_str = day_str.replace('-', '/')
        log_time = day_str + ' ' + time_str + '.' + usecs_str
        d = datetime.datetime.strptime(log_time, '%Y/%m/%d %H:%M:%S.%f')
        ts = d.timestamp()

        usecs, secs = math.modf(ts)
        usecs = usecs * 1e6
        return int(secs), int(usecs)