#!/usr/bin/env python3

#
# Looks for message "sequences" in a log.
#
# It's not really a proper sequence... but I couldn't think of the right term
# on a lazy Sunday.
#
# The "sequence" of messages to look for is defined by a graph. The graph
# is meant to mimic a debugging decision tree. For example, in a FunOS
# log the following sequence means COMe probably got stuck as a result of
# a FunOS crash:
#     saw COMe powering up message -> did not see COMe enumeration message ->
#     saw FunOS bug_check
#
# In some cases the decision tree is the reverse of how we actually debug
# because we work backwards from the explosion. e.g.
#     saw ARP timeout <- did not see management port enabled message
#
# It should be possible to simplify the creation of the decision graphs with
# some type of DSL, maybe even python fragments. At the moment, specifying
# the JSON can be painful and error-prone.
#
# Usage: scan_log.py -h
#
# Copyright (c) 2020 Fungible Inc.  All rights reserved.
#

import argparse
import collections
import json
import re


class Edge(object):
    """
    An edge in the decision graph.

    The edge can be traversed if any of the conditions (which are
    treated as regex patterns) match the log line.
    """
    def __init__(self, dst, conditions):
        self.dst = dst
        self.conditions = conditions

    @staticmethod
    def from_json(js):
        return Edge(js['next_state'], js['conditions'])


class DecisionGraph(object):
    """
    Makes traversal decisions based on the log lines encountered and the
    current state (it's a Moore machine, really?!).

    Assumes the starting point is a node named 'start'.
    """
    def __init__(self, gid):
        self.id = gid
        self.adj = collections.defaultdict(list)
        self.state = 'start'

        self.report_by_node = dict()

    def add_report(self, node, report):
        """
        A node report is relevant if, after reading all lines, we end on
        that node.
        """
        self.report_by_node[node] = report

    def add_edge(self, src, edge):
        adj_list = self.adj[src]
        adj_list.append(edge)

    def try_advance_state(self, line):
        """ The function to call for each line """
        edges = self.adj[self.state]

        for edge in edges:
            for cond in edge.conditions:
                if re.search(cond, line):
                    self.state = edge.dst
                    return

    def get_report(self):
        """
        Gets the report, or None if the node isn't interesting.

        Returns a tuple of (graph_id, report)
        """
        if self.report_by_node.get(self.state):
            return self.id, self.report_by_node[self.state]
        return self.id, None

    @staticmethod
    def from_json(json_graph):
        """ Builds a decision graph from its JSON serialization. """
        g = DecisionGraph(json_graph['id'])

        for json_report in json_graph['reports']:
            g.add_report(json_report['state'], json_report['report'])

        for json_edge in json_graph['transitions']:
            edge = Edge.from_json(json_edge)
            g.add_edge(json_edge['state'], edge)

        return g


class LogScanner(object):
    """
    Traverses the decision graphs and returns reports at the end.
    """
    def __init__(self):
        self.graphs = []

    def add_graph(self, g):
        """ Add a decision graph """
        self.graphs.append(g)

    def scan(self, fh):
        """ Walks through all lines in fh and returns any reports """
        reports = []

        for line in fh:
            for graph in self.graphs:
                graph.try_advance_state(line)

        for graph in self.graphs:
            report = graph.get_report()
            if report[1]:
                reports.append(report)

        return reports


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('log', type=str, help='Log file to parse')
    parser.add_argument('msgs', type=str, help='Message JSON file')
    args = parser.parse_args()

    scanner = LogScanner()
    with open(args.msgs, 'r') as fh:
        js = json.load(fh)
        for json_graph in js:
            g = DecisionGraph.from_json(json_graph)
            scanner.add_graph(g)

    with open(args.log, 'r') as fh:
        reports = scanner.scan(fh)

        for r in reports:
            print('{}: {}'.format(r[0], r[1]))


if __name__ == '__main__':
    main()

