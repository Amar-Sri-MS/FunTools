#!/usr/bin/env python3

import os, sys, logging, glob
from jinja2 import Template
from jinja2 import Environment
from jinja2 import FileSystemLoader
import datetime
import subprocess
import struct
import tempfile
import json
import jsonutils
import argparse

logger = logging.getLogger('mod_interface')
logger.setLevel(logging.INFO)

class ModInterfaceGen():
    tmpl = 'mod_interface_h.j2'

    def __init__(self, input_file, output_file):
        self.output_file = output_file
        self.input_file = input_file
        self.data = jsonutils.load_fungible_json(input_file)


    def generate_interface_header(self):
        date = datetime.datetime.now()
        this_dir = os.path.dirname(os.path.abspath(__file__))
        meta_data = {
            'date' : date.strftime("%x"),
            'year' : date.year,
            'generator' : os.path.basename(os.path.abspath(__file__)),
            'filename': os.path.basename(self.input_file),
        }

        data = list()

        for v in list(self.data.values()):
            for v1 in list(v.values()):
                data.append(v1)

        env = Environment(
            loader=FileSystemLoader(this_dir),
            trim_blocks=True,
            lstrip_blocks=True)
        tmpl = env.get_template(self.tmpl)

        with open(self.output_file, 'w') as f:
            f.write(tmpl.render(
                data=data,
                meta_data=meta_data))

    def generate_interface_json(self):
        # convert module interface json to a json dict that can
        # be embedded in FunOS config to allow reading descriptions
        # for interface values
        # The expected output is going to be available as
        # modulepath/key/[value]/description
        # For enum lists in input json that means they need to be converted
        # from a list into a dict and value will be used as a key entry
        # as the enum values may be sparse so keeping them directly as a list
        # is not good for later reads.
        # Other types (non-enum) are currently not implemented.
        res = {}
        for k,v in list(self.data.items()):
            res1 = {}
            for entry, value in list(v.items()):
                res2 = {}
                assert value['type'] == 'enum'
                id = 0
                for item in value['values']:
                    item_id = item.get('value')
                    if item_id is None:
                        item_id = id
                    res2[item_id] = item['description']
                    id = item_id + 1
                res1[entry] = res2

            res[k] = res1

        with open(self.output_file, 'w') as f:
            json.dump({'module_interfaces':res}, f, indent=4)

    @staticmethod
    def get_build_deplist():
        this_dir = os.path.dirname(os.path.abspath(__file__))
        templates = [ ModInterfaceGen.tmpl ]
        return [os.path.join(this_dir, tmpl) for tmpl in templates]


def main():
    arg_parser = argparse.ArgumentParser(
        description="Module interface description parser")

    arg_parser.add_argument("--print-build-deps", action='store_true',
                            help="Print build dependencies")

    # Check print-build-deps arg initially, so that it can be used
    # without the other mandatory arguments added later on
    args, _ = arg_parser.parse_known_args()
    if args.print_build_deps:
        print(' '.join(ModInterfaceGen.get_build_deplist()))
        return 0

    arg_parser.add_argument("--in-file", required=True, help="input file")
    arg_parser.add_argument("--out-file", required=True, help="output file")
    arg_parser.add_argument("--format", required=True, choices=["header", "json"])

    args = arg_parser.parse_args()

    mi = ModInterfaceGen(args.in_file, args.out_file)

    if args.format == 'json':
        mi.generate_interface_json()
    elif args.format == 'header':
        mi.generate_interface_header()


if __name__ == "__main__":
    main()
