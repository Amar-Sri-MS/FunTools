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

    def __str__(self):
        s = ""
        for node in self.nodes:
            s += "{}: {}\n".format(node.id, node.name)

        for i, edges in enumerate(self.adj_list):
            s += "{}: {}\n".format(i, edges)
        return s


class CGraphStackCheck:
    def __init__(self, cgraph):
        self.cgraph = cgraph

    def _reset(self):
        self.visited = set()
        self.completed = set()

    def check(self, root_id):
        self._reset()
        su, culprits = self.dfs(root_id)
        return su, culprits

    def dfs(self, root_id):
        if root_id in self.visited:
            print(
                "Cycle detected for {} : probable recursion?".format(
                    self.cgraph.nodes[root_id]
                )
            )
            for v in self.visited:
                print("Cycle member: {}".format(self.cgraph.nodes[v]))
            return 0, []

        max_su = 0
        max_culprits = []

        self.visited.add(root_id)
        neighbours = self.cgraph.adj_list[root_id]
        for n in neighbours:
            su, culprits = self.dfs(n)
            if su > max_su:
                max_su = su
                max_culprits = culprits

        self.visited.remove(root_id)
        self.completed.add(root_id)

        max_culprits.append(root_id)
        max_su += self.cgraph.nodes[root_id].stack_usage
        return max_su, max_culprits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("objdir", type=str, help="path to obj directory with .ci files")
    parser.add_argument("function", type=str, help="function name as in .ci file")
    args = parser.parse_args()

    cgraph = CGraph()
    files = glob.glob(os.path.join(args.objdir, "**/*.ci"), recursive=True)
    print(files)
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

    print(cgraph)

    sc = CGraphStackCheck(cgraph)
    su, culprits = sc.check(cgraph.get_node(args.function).id)

    print("Stack usage: {}".format(su))
    for culprit in reversed(culprits):
        cn = cgraph.nodes[culprit]
        print("\t{}\t{}".format(cn.stack_usage, cn.name))


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
