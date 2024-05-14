#!/usr/bin/env python3

#
# Estimates maximum stack usage by traversing call graphs
# generated by gcc's -fcallgraph-info=su option.
#
# Not foolproof, known issues include inability to handle
# cycles in the graph. Recursion is one example.
#
import argparse
import glob
import os
import re


class Node:
    def __init__(self, name, stack_usage):
        self.name = name
        self.stack_usage = stack_usage
        self.id = -1
        self.dummy = False

    def set_id(self, id):
        self.id = id

    @staticmethod
    def from_line(line):
        m = re.match('.*title: "(.*)" label: "(.*)"', line)
        if m:
            name = m.group(1)
            label = m.group(2)
            su = Node._extract_stack_usage(label)
            return Node(name, su)
        return None

    def _extract_stack_usage(label):
        m = re.match(".*?([\d]+) bytes", label)
        if m:
            return int(m.group(1))
        return 0

    def __str__(self):
        return "{} {}".format(self.id, self.name)


class CGraph:
    def __init__(self):
        self.nodes_by_name = {}
        self.nodes = []
        self.adj_list = []

    def add_node(self, node):
        self.nodes_by_name[node.name] = node
        self.nodes.append(node)
        self.adj_list.append(list())

        node_id = len(self.adj_list) - 1
        node.set_id(node_id)

    def replace_node(self, node):
        old_node = self.nodes_by_name[node.name]
        node.set_id(old_node.id)
        self.nodes[old_node.id] = node
        self.nodes_by_name[node.name] = node

    def get_node(self, name):
        return self.nodes_by_name.get(name)

    def add_edge(self, start, end):
        self.adj_list[start.id].append(end.id)

    def get_roots(self):
        root_table = {}
        for node in self.nodes:
            root_table[node.id] = True

        for nbs in self.adj_list:
            for neighbour in nbs:
                root_table[neighbour] = False

        roots = set()
        for node in root_table:
            if root_table[node]:
                roots.add(node)
        return roots

    def __str__(self):
        s = ""
        for node in self.nodes:
            s += "{}: {}\n".format(node.id, node.name)

        for i, edges in enumerate(self.adj_list):
            s += "{}: {}\n".format(i, edges)
        return s


class CGraphStackCheck:
    def __init__(self, cgraph, report_cycles, wutrace_enabled, mtracker_enabled):
        self.cgraph = cgraph
        self.report_cycles = report_cycles
        self.wutrace_enabled = wutrace_enabled
        self.mtracker_enabled = mtracker_enabled

        # Each augmentation is a tuple of:
        #   - maximum stack usage including this node
        #   - index of the max path child
        self.augmented_nodes = {}
        self._reset()

    def _reset(self):
        # dictionary because the cpython implementation
        # is insertion-ordered which is nice for printing
        # cycles
        self.visited = {}
        self.completed = set()

    def check(self, root_id):
        self._reset()
        su = self.dfs_callgraph(root_id)
        path = self.build_path(root_id)
        return su, path

    def build_path(self, root_id):
        path = [root_id]
        node_id = root_id
        _, max_child = self.augmented_nodes[node_id]
        while max_child != -1:
            neighbours = self.cgraph.adj_list[node_id]
            node_id = neighbours[max_child]
            path.append(node_id)
            _, max_child = self.augmented_nodes[node_id]
        return path

    def dfs_callgraph(self, root_id):
        if root_id in self.completed:
            return self.augmented_nodes[root_id][0]

        if root_id in self.visited:
            if self.report_cycles:
                self.print_cycle(root_id)
            return 0

        max_su = 0
        max_idx = -1

        self.visited[root_id] = True
        neighbours = self.cgraph.adj_list[root_id]
        for idx, n in enumerate(neighbours):
            if not self.wutrace_enabled and self.is_wutrace_node(n):
                continue
            if not self.mtracker_enabled and self.is_mtracker_node(n):
                continue
            su = self.dfs_callgraph(n)
            if su > max_su:
                max_su = su
                max_idx = idx

        del self.visited[root_id]
        self.completed.add(root_id)
        max_su += self.cgraph.nodes[root_id].stack_usage
        self.augmented_nodes[root_id] = (max_su, max_idx)
        return max_su

    def print_cycle(self, root_id):
        print(
            "Cycle detected for {} : probable recursion?".format(
                self.cgraph.nodes[root_id]
            )
        )
        for v in self.visited:
            print("Cycle member: {}".format(self.cgraph.nodes[v]))

    def is_wutrace_node(self, node_id):
        node = self.cgraph.nodes[node_id]
        return node.name == "trace_wu_send"

    def is_mtracker_node(self, node_id):
        node = self.cgraph.nodes[node_id]
        return node.name in [
            "fun_mtracker_record_alloc_multiple",
            "fun_mtracker_record_alloc",
            "full_stack_here",
        ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("objdir", type=str, help="path to obj directory with .ci files", nargs="+")
    parser.add_argument(
        "--function", type=str, help="print stack path for function name as in .ci file"
    )
    parser.add_argument(
        "--report-cycles", action="store_true", help="report cycles in graph"
    )
    # wu tracing adds a significant amount of C-stack, so make
    # it opt-in when determining usage.
    parser.add_argument(
        "--wutrace-enabled", action="store_true", help="assume wu tracing is enabled"
    )
    parser.add_argument(
        "--mtracker-enabled", action="store_true", help="assume mtracker is enabled"
    )

    args = parser.parse_args()

    cgraph = CGraph()
    files = []
    for objdir in args.objdir:
        files.extend(glob.glob(os.path.join(objdir, "**/*.ci"), recursive=True))

    # Two pass approach: nodes then edges
    for f in files:
        fh = open(f, "r")
        for line in fh:
            add_node_to_graph(cgraph, line)

    for f in files:
        fh = open(f, "r")
        for line in fh:
            try:
                add_edge_to_graph(cgraph, line)
            except:
                print(f, line)

    sc = CGraphStackCheck(
        cgraph, args.report_cycles, args.wutrace_enabled, args.mtracker_enabled
    )

    if args.function:
        print_worst_case_path(args.function, cgraph, sc)
    else:
        print_top_users(cgraph, sc)


def print_worst_case_path(func_name, cgraph, stack_check):
    su, culprits = stack_check.check(cgraph.get_node(func_name).id)

    print("Stack usage: {}".format(su))
    running_sum = 0
    print("\t{}\t{}\t{}".format("Local", "Cumulative", "Name"))
    for culprit in culprits:
        cn = cgraph.nodes[culprit]
        running_sum += cn.stack_usage
        print("\t{}\t{}\t\t{}".format(cn.stack_usage, running_sum, cn.name))


def print_top_users(cgraph, stack_check):
    roots = cgraph.get_roots()

    top_count = 100
    su_and_root = []
    for node in cgraph.nodes:
        if node.id not in roots:
            continue
        su, _ = stack_check.check(node.id)
        su_and_root.append((su, node.name))

    su_and_root.sort()
    su_and_root.reverse()
    print("Top stack users")
    for i in range(top_count):
        su, node_name = su_and_root[i]
        print("{}\t{}".format(su, node_name))


def add_node_to_graph(cgraph, line):
    if not line.startswith("node"):
        return

    node = Node.from_line(line)
    existing_node = cgraph.get_node(node.name)
    if existing_node:
        # Prefer nodes with stack usage
        replace = node.stack_usage != 0
        if replace:
            cgraph.replace_node(node)
    else:
        cgraph.add_node(node)


def add_edge_to_graph(cgraph, line):
    if not line.startswith("edge"):
        return
    start, end = parse_edge(line)
    snode = cgraph.get_node(start)
    enode = cgraph.get_node(end)

    if snode is None:
        print("Creating dummy start for {}".format(line))
        snode = create_dummy_node(start, cgraph)
    if enode is None:
        print("Creating dummy end for {}".format(line))
        enode = create_dummy_node(end, cgraph)
    cgraph.add_edge(snode, enode)


def parse_edge(line):
    m = re.match('.*sourcename: "(.*?)" targetname: "(.*?)"', line)
    if m:
        return m.group(1), m.group(2)
    return None, None


def create_dummy_node(name, cgraph):
    node = Node(name, 0)
    node.dummy = True
    cgraph.add_node(node)
    return node


def check_duplicates(cgraph):
    """
    Just an eyeball check to see if the compiler gave
    almost similar names to the same node.
    """
    names = []
    for name in cgraph.nodes_by_name:
        names.append(name)

    for i in range(len(names) - 1):
        for j in range(i + 1, len(names)):
            if names[i] in names[j]:
                print(names[i], names[j])
            if names[j] in names[i]:
                print(names[j], names[i])


if __name__ == "__main__":
    main()
