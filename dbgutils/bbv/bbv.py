#
#  bbv.py
#
#  Created by Hariharan Thantry on 2019-02-28
#
#  Copyright 2019 Fungible Inc. All rights reserved.
#

#!/usr/bin/env python3


import argparse
import collections
import pdb
import re
import sys

#from graph import Grapher
from .histogram import Histogram

# Instructions belong to a basic block
class BasicBlock(object):
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr
        self.icount = 0
        self.insns = []

    def add_instr(self, instr):
        self.insns.append(instr)
        self.icount += 1
    def __str__(self):
        m_str = "{}:{}".format(self.name, self.icount)
        return m_str

    __repr__ = __str__

class BB_Analyze(object):
    def __init__(self):

        self.bbs_re_full = \
                re.compile("^([0-9a-fA-F]+) <([\$\.\w_0-9]+)>:\s*$")
        self.bbs_re_compiler = \
                re.compile("^([0-9a-fA-F]+) <[\$\.]L([\$\w_0-9]+)>:\s*$")
        self.bbs_re_func = \
                re.compile("^([0-9a-fA-F]+) <([\$\w_0-9]+)>:\s*$")

        self.current_bbs = {}
        self.ignore_bbs = 0
        self.total_bbs = 0

    def __get_bb(self, line, only_func):
        this_bb = None
        if only_func:
            re_match = self.bbs_re_func.match(line)
        else:
            re_match = self.bbs_re_full.match(line)

        if re_match:
            if only_func and self.bbs_re_compiler.match(line):
                return this_bb

            m_name = re_match.group(2)
            i_cnt = 0
            if m_name not in self.current_bbs:
                self.current_bbs[m_name] = i_cnt
            else:
                i_cnt = self.current_bbs[m_name]
                i_cnt += 1
            self.current_bbs[m_name] = i_cnt
            m_name = "{}.{}".format(m_name, i_cnt)
            this_bb = BasicBlock(m_name, re_match.group(1))

        return this_bb

    def __get_instr(self, line):
        l_arr = [x.strip() for x in line.split(':')]
        if len(l_arr) != 2:
            return None
        try:
            int(l_arr[0], 16)
            return l_arr
        except ValueError:
            return None

    def __summarize(self, hist, x_len):
        m_hist = collections.OrderedDict()
        for key, val in hist.items():
            m_hist[key/x_len] = m_hist.get(key/x_len, 0) + val
        return m_hist

    def __hist(self, o_hist, bbv_img):
        hist = collections.OrderedDict(sorted(o_hist.items()))
        instr_cnt_per_bucket = 1
        if self.bbs_max_val > 40:
            max_val = list(hist.keys())[-1]
            instr_cnt_per_bucket = max_val/40
            hist = self.__summarize(hist, instr_cnt_per_bucket)

        columns=['icount', 'freq']
        x_label = "bb_isize, icount={}".format(instr_cnt_per_bucket)
        y_label = "Frequency"
        lbls = [x_label, y_label]
        ignored = (float(self.ignore_bbs) *100)/(float(self.total_bbs))
        title='BBV<={}:Ignored {:.2f}%'.\
                        format(self.bbs_max_val, ignored)
        Histogram().plot(hist, columns, lbls, title, bbv_img)

    def __compute_hist(self, bbs):
        hist = collections.OrderedDict()
        for bb in bbs:
            if not bb.icount:
                continue
            self.total_bbs += 1
            if bb.icount > self.bbs_max_val:
                self.ignore_bbs += 1

                continue
            hist[bb.icount] = hist.get(bb.icount, 0) + 1
        return hist

    def analyze(self, dump_file, bbv_img=None, only_func=False):
        curr_bb = None
        bbs = []
        matched = False
        if only_func:
            self.bbs_max_val = 256
        else:
            self.bbs_max_val = 20
        # First slurp in all the lines in the dump_file
        with open(dump_file, "r") as txt:
            for line in txt:
                bb = self.__get_bb(line, only_func)
                if not bb:
                    instr = self.__get_instr(line)
                    if not instr:
                        continue
                    curr_bb = bbs[-1]
                    assert curr_bb != None, "No current basic block to add instruction to"
                    curr_bb.add_instr(instr)
                else:
                    bbs.append(bb)
        hist = self.__compute_hist(bbs)
        self.__hist(hist, bbv_img)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("python bbv.py dump_file [png_file=None] [only_func=0]")
        sys.exit(0)
    p = BB_Analyze()
    g = len(sys.argv)
    only_func = False
    bbv_img = None
    if g > 3:
        only_func = sys.argv[3]
    elif g > 2:
        bbv_img = sys.argv[2]

    p.analyze(sys.argv[1], bbv_img, only_func)
