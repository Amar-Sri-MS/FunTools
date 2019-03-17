#!/usr/bin/env python2.7

#
# Scrapes various bits of performance-related information from a
# FunOS log and writes a JSON file.
#
# The JSON type is an array of objects ordered by increasing fabric
# address and looks like this:
#
# [ { metricA: valueA0, metricB: valueB0, faddr: {faddr0} },
#   { metricA: valueA0, metricB: valueB1, faddr: {faddr1} },
#   ... ]
#
# Usage: parse_funos_log.py <input_file> [-o <output_file>]
#
# The default output file is named stats_summary.json.
#

import re
import json
import argparse


class FAddr:
    """
    Represents a fabric address (GID:LID:Q).
    GID is the cluster, LID is the VP and Q is the queue
    """
    def __init__(self, gid, lid, q):
        self.gid, self.lid, self.q = gid, lid, q

    def __str__(self):
        return str(self.gid) + ":" \
               + str(self.lid) + ":" \
               + str(self.q)

    def to_dict(self):
        return {
            'gid' : self.gid,
            'lid' : self.lid,
            'queue' : self.q,
        }


class StatEntry:
    """
    Statistics for a particular fabric address
    """
    def __init__(self, f_addr, sent, recvd, util_pct):
        self.f_addr = f_addr
        self.sent, self.recvd, self.util_pct = sent, recvd, util_pct

    def to_dict(self):
        return {
            'faddr' : self.f_addr.to_dict(),
            'wus_sent' : self.sent,
            'wus_recvd' : self.recvd,
            'util_pct' : self.util_pct,
        }


class LogParser:
    """
    Parses a FunOS run log looking for performance-related statistics
    """
    def __init__(self):
        self.stats = []
        self.pattern = re.compile(r'.*nucleus.*FA(\d+):(\d+):(\d+).*sent\s+(\d+).*recv\s+(\d+)\s+WUs\s+(\d+\.\d+).*')

    def parse_line(self, line):
        """
        Parses a line from a FunOS log, extracting the GID, LID, Q and
        % utilization and WU counts. We assume that the information is
        logged in ascending fabric address order, so the GIDs and LIDs
        are also in ascending order.
        :param line:
        :return: None
        """
        match = self.pattern.match(line)
        if match:
            f_addr = FAddr(int(match.group(1)),
                           int(match.group(2)),
                           int(match.group(3)))
            stat = StatEntry(f_addr,
                             int(match.group(4)),
                             int(match.group(5)),
                             float(match.group(6)))
            self.stats.append(stat)

    def json_str(self):
        """
        :return: JSON containing stats or None if no stats were found
        """
        if self.stats:
            list_of_dicts = [s.to_dict() for s in self.stats]
            return json.dumps(list_of_dicts)
        else:
            return None


def main():
    """
    Entry point for the script.
    Side effects: Reads a file. Writes a file if data has been collected.
    :return: None
    """
    argparser = argparse.ArgumentParser()
    argparser.add_argument('input_file', type=str, help='path to input file')
    argparser.add_argument('-o', '--output_file', type=str,
                           help='path to output file',
                           default='stats_summary.json')
    args = argparser.parse_args()

    with open(args.input_file, 'r') as fh:
        parser = LogParser()
        for line in fh.readlines():
            parser.parse_line(line)

    result = parser.json_str()
    with open(args.output_file, 'w') as fh:
        if result is not None:
            fh.write(result)


if __name__ == '__main__':
    main()
