#
#  orchestrator.py
#
#  Created by Hariharan Thantry on 2019-03-08
#
#  Copyright 2019 Fungible Inc. All rights reserved.
#

#!/usr/bin/env python3

import argparse
import re
import sys

from .bbv import BB_Analyze

class Orchestrator():
    def __init__(self, argv):
        parser = argparse.ArgumentParser(description='Analze ELF MIPS64 binary through artifact generation')
        parser.add_argument("-g", "--graph", action='store_true', help="Generate the control flow forest/graph")
        parser.add_argument("-b", "--bbv", action='store_true', help="Do histogram of basic block vector lengths")
        parser.add_argument("-o", "--out_file", help="PNG file to store the histogram")
        parser.add_argument("-f", "--only-functions", action='store_true', help="Filter to include only functions in basic blocks & graphs")
        parser.add_argument("-w", "--wu-file", help="Filter file that consists of the list of functions to trace for call graph. Each WU becomes a different file")
        parser.add_argument("-i", "--in-file", help="objdump file of MIPS64 binary")
        self.args = parser.parse_args()
    
    def run(self):
        if not self.__check_file(self.args.in_file):
            return
        if self.args.bbv:
            p = BB_Analyze().analyze(self.args.in_file, 
                    self.args.out_file,
                    self.args.only_functions)
        if self.args.graph:
            print("Graphing not implemented. Please see README for alternatives")
            sys.exit(0)

    def __identify(self, line):
        f_format = re.search('file format ([\w\-]+)', line)
        m_type = None
        if f_format:
            m_type = f_format.group(1)
        return m_type

    def __check_file(self, dump_file):
        m_type = None
        if not dump_file:
            assert False, "No dump file supplied"

        with open(dump_file, "r") as txt:
            for line in txt:
                m_type = self.__identify(line)
                if m_type:
                    if m_type != "elf64-bigmips":
                        print("Only support elf64-bigmips")
                        return False
                    else:
                        return True
        return m_type

if __name__ == '__main__':
    p = Orchestrator(sys.argv)
    p.run()

