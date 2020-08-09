#
# Various file input blocks.
#
# The hope is that at some point, once we have a real log ingestion scheme
# that uses flume, syslog-ng, the ELK stack or something else, that this
# will simplify into reading the output data (or maybe even a search
# query) from that ingestion scheme.
#
# But till then... we have to play its role.
#

import datetime
import io
import math
import os

from blocks.block import Block


class FileInput(Block):
    """ Base class for file input blocks """

    def __init__(self):
        self.file = None
        self.env = {}
        self.uid = None

    def set_config(self, cfg):
        self.env = cfg['env']
        self.file = cfg['file']
        self.uid = cfg['uid']


class FunOSInput(FileInput):
    """ Handles FunOS log files """
    def __init__(self):
        super().__init__()

    def process(self, iters):
        logdir = self.env['logdir']
        path = self.file.replace('${logdir}', logdir)

        return self.lines2tuples(path)

    def lines2tuples(self, path):
        uboot_done = False

        with io.open(
                os.path.expandvars(path), 'r', encoding='ascii', errors='replace'
        ) as f:
            for line in f:
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

                    yield (secs, usecs, self.uid, None, line)

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


class ISOFormatInput(FileInput):
    """ Handles logs with ISO format timestamps """

    def __init__(self):
        super().__init__()

    def process(self, iters):
        logdir = self.env['logdir']
        path = self.file.replace('${logdir}', logdir)

        with io.open(
                os.path.expandvars(path), 'r', encoding='ascii', errors='replace'
        ) as f:
            for line in f:
                line = line.strip()

                # Example:
                # 2020-07-09 16:37:59.240281 Start probing thread
                parts = line.split(' ', 2)

                iso_format_datetime = parts[0] + ' ' + parts[1]
                d = datetime.datetime.fromisoformat(iso_format_datetime)

                ts = d.timestamp()
                secs, usecs = self.normalize_ts(ts)

                yield (secs, usecs, self.uid, None, parts[2])

    @staticmethod
    def normalize_ts(ts):
        useconds, seconds = math.modf(ts)
        return int(seconds), int(useconds * 1e6)
