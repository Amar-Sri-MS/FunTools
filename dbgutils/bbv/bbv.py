#
#  bbv.py
#
#  Created by Hariharan Thantry on 2019-02-28
#
#  Copyright 2019 Fungible Inc. All rights reserved.
#

#!/usr/bin/env python


import argparse
import collections
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import pdb
import re
import sys

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

class Analyze(object):
    def __init__(self, args):
        self.bbs_re = re.compile("^([0-9a-fA-F]+) <([\$\.\w_0-9]+)>:\s*$")
        self.current_bbs = {}
        self.ignore_bbs = 0
        self.total_bbs = 0
        self.__analyze(args)

    def __get_bb(self, line):
        this_bb = None
        re_match = self.bbs_re.match(line)
        if re_match:
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
    def __ascii(self, hist):
        for k in sorted(hist.keys()):
            print "{0:5d} {1}".format(k, hist[k])


    def __summarize(self, hist, x_len):
        m_hist = collections.OrderedDict()
        for key, val in hist.iteritems():
            m_hist[key/x_len] = m_hist.get(key/x_len, 0) + val
        return m_hist

    def __show_on_bars(self, axs):
        for p in axs.patches:
            _x = p.get_x() + p.get_width()/2
            _y = p.get_y() + p.get_height()
            val = '{}'.format(int(p.get_height()))
            axs.text(_x, _y, val, ha="center")


    def __hist(self, o_hist, bbv_img):
        hist = collections.OrderedDict(sorted(o_hist.items()))

        # This loads in the key-value pairs into a Panda dataframe
        a4_dims = (20, 10)
        fig, ax = plt.subplots(figsize=a4_dims)
        df = pd.DataFrame(list(hist.items()), columns=['icount', 'freq'])

        sns.set_context("paper")
        sns.set_style("whitegrid")

        sns_plot = sns.barplot(x='icount',
                   y='freq',
                   data=df,
                   ax=ax
                   )

        ignored = (float(self.ignore_bbs) *100)/(float(self.total_bbs))
        sns_plot.set(xlabel='BBV Length',
                ylabel='Frequency',
                Title='BBV<=20:Ignored {:.2f}%'.format(ignored))

        self.__show_on_bars(ax)
        fig.savefig(bbv_img)

    def __compute_hist(self, bbs):
        hist = collections.OrderedDict()
        for bb in bbs:
            if not bb.icount:
                continue
            self.total_bbs += 1
            if bb.icount > 20:
                self.ignore_bbs += 1

                continue
            hist[bb.icount] = hist.get(bb.icount, 0) + 1
        return hist

    def __do_hist(self, dump_file, bbv_img):
        curr_bb = None
        bbs = []
        # First slurp in all the lines in the dump_file
        with open(dump_file, "r") as txt:
            for line in txt:
                bb = self.__get_bb(line)
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


    def __analyze(self, args):
        if args.bbv:
            self.__do_hist(args.dump_file, args.bbv)


class Program():
    def __init__(self, args):
        parser = argparse.ArgumentParser(description='Analze ELF MIPS64 binary through artifact generation')
        parser.add_argument("-g", "--graph", action='store_true', help="Generate the control flow forest/graph")
        parser.add_argument("-b", "--bbv", help="Histogram the basic block vector lengths")
        parser.add_argument("-f", "--only-functions", action='store_true', help="Filter to include only functions in basic blocks & graphs")
        parser.add_argument("-w", "--wu-file", help="Filter file that consists of the list of wus to trace for call graph. Each WU becomes a different file")
        parser.add_argument("-x", "--dump-file", help="objdump file of MIPS64 binary")
        args = parser.parse_args()
        Analyze(args)



if __name__ == '__main__':
    p = Program(sys.argv)


