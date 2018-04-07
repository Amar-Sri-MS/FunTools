#
#  csr_main.py
#
#  Created by Hariharan Thantry on 2018-02-21
#
#  Copyright 2018 Fungible Inc. All rights reserved.
#
# Top level main python package

import argparse
import os
from module_path import module_locator
from csr.utils.yml import YML_Reader, CSR_YML_Reader
from csr.utils.artifacts import CSRRoot, Walker, RingUtil, TmplMgr

class Slurper(object):
    def __init__(self, cwd):
        self.cwd = cwd
        #self.cmd_parser = argparse.ArgumentParser(description="CSR Slurper utility for F1")
        self.other_args = {}
        #self.__arg_process(self.cmd_parser, self.other_args)
        print "Started Slurper"

    def __arg_process(self, cmd_parser, other_args):
        ml_dir = module_locator().module_path()
        def_dir = os.path.join(ml_dir, "csr_cfg")
        cmd_parser.add_argument("-i", "--csr-defs", help="CSR definitions",
                default=def_dir, required=False, type=str)

        cmd_parser.add_argument("-o", "--gen-cc", help="Dir for the C++ files.",
                required=True, type=str)
        self.other_args['tmpl_file'] = os.path.join(ml_dir, "template", "csr_rt.j2")

        cmd_parser.add_argument("-r", "--match-ring", help="Generate for ring pattern",
                default="nu", required=False, type=str)


    def __update_loc(self, loc):
        if not os.path.isabs(loc):
            loc = os.path.join(self.cwd, loc)
        assert os.path.exists(loc), "{}: directory does not exist".format(loc)
        return loc

    def __check_yml_dir(self, y_dir):
        yml_dir = os.path.join(y_dir, "inc")
        if not os.path.exists(yml_dir):
            assert False, "Yaml directory: {} does not exist".format(yml_dir)

        if not os.path.isdir(yml_dir):
            assert False, "Yaml: {} not a directory".format(yml_dir)
        if not os.path.exists(os.path.join(y_dir, "AMAP")):
            assert False, "AMAP file does not exist"
        #if not os.path.exists(os.path.join(y_dir, "ringAN.yaml")):
        #    assert False, "Ring file does not exist"

    def run(self):
        #args = self.cmd_parser.parse_args()
        #args.csr_defs = self.__update_loc(args.csr_defs)
        #args.gen_cc = self.__update_loc(args.gen_cc)

        #self.__check_yml_dir(args.csr_defs)
        #yml_dir = os.path.join(args.csr_defs, "csr/csr-cfg/inc")
        #amap_file = os.path.join(args.csr_defs, "csr/csr-cfg/MAP")
        #ring_file = os.path.join(args.csr_defs, "csr/csr-cfg/ringAN.yaml")
        yml_dir = "csr/csr_cfg/inc"
        amap_file = "csr/csr_cfg/AMAP"
        ring_file = "csr/csr_cfg/ringAN.yaml"

        schema = CSR_YML_Reader(yml_dir)
        #print "{}".format(self.schema)
        # First populate the top level root
        # Only populates the address attribute
        #print("%s %s") %(amap_file, args.match_ring)
        #csr_root = CSRRoot(amap_file, schema.get(), args.match_ring)
        csr_root = CSRRoot(amap_file, schema.get(), "")
        print "NAG 1**********"
        #tmpl = TmplMgr(self.other_args['tmpl_file'])
        tmpl = TmplMgr("csr/template/csr_rt.j2")
        print "NAG 2**********"
        #o_file = os.path.join(args.gen_cc, 'csr_gen.cpp')
        o_file = 'csr_gen.cpp'
        print "NAG 3**********"
        #if csr_root is not None:
        #    print csr_root.get_map()
        print "NAG 4**********"
        tmpl.write_cfg(o_file, csr_root)

        # Next, get the ring structure
        #p = YML_Reader()
        #yml_stream = p.read_file(ring_file)
        #w = Walker(yml_stream)
        #print "{}".format(w)
        return csr_root



    def __str__(self):
        r_str = "{}".format(self.schema)
        return r_str

    __repr__ = __str__



