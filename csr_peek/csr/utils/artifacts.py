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

class CSRRoot(object):
    START_RING = r'START_RING:'
    END_RING = r'END_RING'

    def __init__(self, amap_file):
        self.in_ring = False
        self.done = False
        self.ring_map = collections.OrderedDict()
        self.__read_update(amap_file)

    def get_map(self):
        return self.ring_map

    def __read_update(self, m_file):
        f = open(m_file, "r")
        for line in f:
            if self.done:
                break
            self.__populate(line)
        f.close()  

    def __populate(self, line):
        if not self.in_ring:
            if re.search(CSRRoot.START_RING, line):
                self.in_ring = True
                return
        if re.search(CSRRoot.END_RING, line):
            self.done = True
            return
        l_arr = line.split()
        if len(l_arr) < 2:
            return
        self.ring_map[l_arr[0]] = self.__hexlify(l_arr[1])
    def __hexlify(self, entry):
        entry = re.sub(r'0x', '', entry)
        entry = re.sub(r'_', '', entry)

        val = int(entry, 16)
        # Only the top 5 bits should be valid
        val &= 0xF800000000
        

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

    def __str__(self):
        r_str = ""
        for elem in self.m_lst:
            r_str += "{}\n".format(elem)
        return r_str
            

