#
#  artifacts.py
#
#  Created by Hariharan Thantry on 2018-02-22
#
#  Copyright 2018 Fungible Inc. All rights reserved.
#
# Process the address map

import collections
import pdb
import re

# For every top level ring, one RingNode object
class RingNode(object):
    def __init__(self, name):
        self.name = name
        self.instances = collections.OrderedDict()
        self.final_ans = collections.OrderedDict()
    def add_instance(self, inst_num, addr):
        assert inst_num not in self.instances
        self.instances[inst_num] = RingProps(self.name, inst_num, addr)
    def add_an(self, inst_num, an_tree):
        assert inst_num in self.instances
        self.instances[inst_num].add_an(an_tree)
    def add_csr(self, an_name, csr_node):
        an = self.final_ans.get(an_name, [])
        an.append(csr_node)
        self.final_ans[an_name] = an
    def __str__(self):
        r_str = "ring_coll_t {}_rng;\n".format(name)
        for m_id, m_node in self.instances.iteritems():
            r_str += "{}_rng.addr_ring({}, 0x{:02X});\n".format(m_id, m_node.get_addr())
            r_str += "{}".format(m_node)

        for an_name, node in self.final_ans.iteritems():
            r_str += "{}".format(node)
            r_str += "add_csr({}, \"{}\", {}".\
                    format(an_name, node.get_name(), node.get_grp());
        return r_str
    __repr__ = __str__



class RingProps(object):
    def __init__(self, r_name, i_num, addr):
        self.r_name = r_name
        self.i_num = i_num
        self.addr = addr;
        self.an_lst = []
    def get_addr(self):
        return self.addr
    def add_an(self, an_tree):
        self.an_lst.append(an_tree);
    def __str__(self):
        r_str = ""
        for an_tree in self.an_lst:
            tree_str = ",".join(an_tree[:-1])
            r_str += "auto {} = {}_rng[{}].add_an({{{}}}, 0x{:02X});\n".\
                    format(an_tree[-2], self.r_name, self.i_num, tree_str, an_tree[-1])
        return r_str
    __repr__ = __str__



class CSRRoot(object):
    START_RING = r'START_RING:'
    END_RING = r'END_RING'



    def __init__(self, amap_file):
        self.in_ring = False
        self.ring_done = False
        self.in_ablk = False
        r_util = RingUtil()
        self.ring_map = collections.OrderedDict()
        self.__read_update(amap_file)

    def get_map(self):
        return self.ring_map

    def __read_update(self, m_file):
        f = open(m_file, "r")
        for line in f:
            if not self.ring_done:
                self.__rings(line)
            else:
                self.__ans(line)

        f.close()


    def add_an(self, r_name, r_inst, an_lst):
        r_node = self.ring_map.get(r_name, None)
        assert r_node != None
        r_node.add_an(r_inst, an_lst)

    def __ans(self, line):
        if not self.in_ablk:




    def __rings(self, line):
        if not self.in_ring:
            if re.search(CSRRoot.START_RING, line):
                self.in_ring = True
                return
        if re.search(CSRRoot.END_RING, line):
            self.ring_done = True
            return
        l_arr = line.split()
        if len(l_arr) < 2:
            return
        ring_class, ring_inst = r_util.get_info(l_arr[0])

        ring_node = self.ring_map.get(ring_class, RingNode(ring_class))
        ring_node.add_instance(ring_inst, self.__hexlify(l_arr[1]))
        self.ring_map[ring_class] = ring_node

    def __hexlify(self, entry):
        entry = re.sub(r'0x', '', entry)
        entry = re.sub(r'_', '', entry)

        val = int(entry, 16)
        # Only the top 5 bits should be valid
        val &= 0xF800000000

    def __str__(self):
        r_str = ""
        for name, node in self.ring_map.iteritems():
            r_str += "{}".format(node)
            r_str += "sys_rings[\"{}\"] = {}_rng;\n".format(name.upper(), name)
        return r_str


    __repr__ = __str__


class RingUtil(self):
    RING_ENC = r'([\w]+)_([\d])+'
    ALT_RING_ENC = r'([\w]+)([\d]+)'
    def __init__(self):
        pass

    def get_info(self, nodename):
        r_grp = re.match(RingUtil.RING_ENC, nodename)
        if not r_grp:
            r_grp = re.match(RingUtil.ALT_RING_ENC, nodename)

        ring_class = r_grp.group(0)
        ring_inst = r_grp.group(1)
        return ring_class, ring_inst


class Walker(object):
    def __init__(self, ring_tree):
        self.m_lst = []
        for val in self.__flatten(ring_tree):
            self.m_lst.append(val)

    def __flatten(self, yml_obj, pre=None):
        pre = pre[:] if pre else []
        if isinstance(yml_obj, dict):
            for key, val in yml_obj.items():
                if isinstance(val, dict):
                    for d in self.__flatten(val, pre + [key]):
                        yield d
                elif isinstance(val, list) or isinstance(val, tuple):
                    for v in val:
                        for d in self.__flatten(v, pre + [key]):
                            yield d
                else:
                    yield pre + [key, val]
        else:
            yield pre + [yml_obj]

    def get_ans(self):
        return self.m_lst

    def __str__(self):
        r_str = ""
        for elem in self.m_lst:
            r_str += "{}\n".format(elem)
        return r_str
    __repr__ = __str__


