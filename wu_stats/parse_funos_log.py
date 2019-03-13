#!/usr/bin/python

#
# Scrapes the total counts of WUs that were sent and received per VP from a
# FunOS log and outputs a JSON file with the information.
#
# Usage: parse_funos_log.py <input_file> [-o <output_file>]
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
    WU statistics for a particular fabric address
    """
    def __init__(self, f_addr, sent, recvd, util_pct):
        self.f_addr = f_addr
        self.sent, self.recvd, self.util_pct = sent, recvd, util_pct

    def to_dict(self):
        return {
            'faddr' : self.f_addr.to_dict(),
            'sent' : self.sent,
            'recvd' : self.recvd,
            'util_pct' : self.util_pct,
        }


class LogParser:
    """
    Parses a FunOS run log looking for WU statistics
    """

    def __init__(self):
        self.stats = []
        self.pattern = re.compile(r'.*nucleus.*FA(\d+):(\d+):(\d+).*sent\s+(\d+).*recv\s+(\d+)\s+WUs\s+(\d+\.\d+).*')

    def parse_line(self, line):
        """
        Parses a line from a FunOS log, extracting the GID, LID, Q and
        WU sent and received counts if present. We assume that the information
        is logged in ascending fabric address order, so the GIDs and LIDs are
        also in ascending order.
        :param line:
        :return: Nothing
        """
        match = self.pattern.match(line)
        if match:
            f_addr = FAddr(match.group(1), match.group(2), match.group(3))
            stat = StatEntry(f_addr, match.group(4), match.group(5),
                             match.group(6))
            self.stats.append(stat)

    def json_str(self):
        """
        :return: JSON format string containing WU stats. If no WU stats were
        found, then a "no_stats" string
        """
        if self.stats:
            list_of_dicts = [s.to_dict() for s in self.stats]
            return json.dumps(list_of_dicts)
        else:
            return "no_stats"


def main():
    """
    Entry point for the script.
    Side effects: reads a file, writes a file
    :return: nothing
    """
    argparser = argparse.ArgumentParser()
    argparser.add_argument('input_file', type=str, help='path to input file')
    argparser.add_argument('-o', '--output_file', type=str, help='path to output file', default='stats.json')
    args = argparser.parse_args()

    with open(args.input_file, 'r') as fh:
        parser = LogParser()
        for line in fh.readlines():
            parser.parse_line(line)

    result = parser.json_str()
    with open(args.output_file, 'w') as fh:
        fh.write(result)


if __name__ == '__main__':
    main()
