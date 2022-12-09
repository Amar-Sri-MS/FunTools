#!/usr/bin/env python3

"""Post process api summary and generate files for following steps

   Copyright (c) 2022 Fungible. All rights reserved.


    Preconditions
    -------------
    FunSDK is up so that sdk headers are available from the current dir (where this script locate) `../../FunSDK/FunSDK/funosrt/include/FunOS/`

    Examples
    --------

    Easier way to run this script is to use `run_gen_api_summary.sh` script instead.

    >>> python ./process_api_summary.py --raw_input test.yml.tmp --proto test.func_proto --output test.yml.processed

    Checks
    ------
    static check:
    >>> mypy ./process_api_summary.py

    format:
    >>> black ./process_api_summary.py

"""

"""
TODO:
- update docstring
- save to html

# NEXT STEP: process_api_summary.py
#
# - check uniqueness
# - check why it is different from the output from ctags, difference of two

(base) insop@mocha [17:44:12] [~/Projects/Fng/FunSDK/FunSDK/funosrt/include] [master] -> % wc -l proto_ctag.txt
3038 proto_ctag.txt

-> % grep '^  -' test.yml.processed| wc -l                        
3040

'''
# docstring
# test

"""

import math
import os
import argparse
from glob import glob
import sys
import yaml
from pathlib import Path
from typing import Iterable, Any, List, Optional, Union, Callable, TextIO, Dict, Tuple

try:
    # for table
    import pandas as pd
except ImportError:
    print("{}: Import failed!".format(__file__))
    print("Install missing modules")
    print(">>> pip install pandas")
    sys.exit()


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw_input",
        type=str,
        help="Raw input file, contains prototypes and other data types",
    )
    parser.add_argument("--proto", type=str, help="Extracted only prototypes")
    parser.add_argument("--output_dir", type=str, default=".", help="Output directory")
    parser.add_argument("--output_yml", type=str, help="Output yml file")
    parser.add_argument("--output_csv", type=str, required=True, help="Output csv file")

    args = parser.parse_args()

    return args


def _load_raw_input(raw_input: str) -> Dict[str, List[str]]:
    """Load config file(s)

    Parameters
    ----------
    config_file : str, optional
        config file path, by default None

    Returns
    -------
    List[Dict[str, str]]
        list of config dict
    """

    print(f"Loding raw input file: {raw_input}")

    with open(raw_input, "r", encoding="utf-8") as f:
        input = yaml.load(f, Loader=yaml.FullLoader)

    return input


def _load_proto(proto: str) -> List[str]:
    # read file and save it as list
    with open(proto, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return lines


def _filter_prototypes(
    raw_input: Dict[str, List[str]], proto: List[str]
) -> Dict[str, List[str]]:
    """Filter prototypes from raw input

    Parameters
    ----------
    raw_input : Dict[str, List[str]]
        raw input
    proto : List[str]
        function prototype list

    Returns
    -------
    Dict[str, List[str]]
        filtered prototypes

    """

    out_dict = {}

    def _if_in_prototype(line: str) -> bool:
        for p in proto:
            if line in p:
                return True
        return False

    def _filter_incomplete_lines(line: str) -> bool:
        if line.startswith("struct") and "(" not in line:
            return True
        if line.startswith("enum") and "(" not in line:
            return True
        if "(" not in line:
            return True
        return False

    for name, prototypes in raw_input.items():
        if prototypes is None:
            continue
        out_dict[name] = []
        for p in prototypes:

            if not _if_in_prototype(p) or _filter_incomplete_lines(p):
                continue
            out_dict[name].append(p)

    return out_dict


def _save_dict_to_yml(data: Dict[str, List[str]], output: str) -> None:
    """Save dict to yml file

    Parameters
    ----------
    data : Dict[str, List[str]]
        data to be saved
    output : str
        output file path
    """

    print(f"Saving to yml file: {output}")

    class MyDumper(yaml.Dumper):
        def increase_indent(self, flow=False, indentless=False):
            return super(MyDumper, self).increase_indent(flow, False)

    with open(output, "w", encoding="utf-8") as f:
        yaml.dump(
            data, f, default_flow_style=False, width=float("inf"), Dumper=MyDumper
        )


def _prepare_table_with_func_prototype(
    data: Dict[str, List[str]], proto: List[str]
) -> List[Dict[str, str]]:
    """
    Prepare table with function prototype
    Table will be prepared in list of dict format
    > [{proto: xxx, filename: xxxx}, ...]

    Parameters
    ----------
    data : Dict[str, List[str]]
        data to be saved
    proto : List[str]
        function prototype list

    Returns
    -------
    List[Dict[str, str]]
        table data
    """

    def _get_proto_name_only(line: str) -> str:
        """Get function name only from prototype

        Parameters
        ----------
        line : str
            prototype

        Returns
        -------
        str
            function name only
        """
        for p in proto:
            if line in p:
                proto_name_only = p.split(" ")[0]
                if proto_name_only[0] == "*":
                    proto_name_only = proto_name_only[1:]
                return proto_name_only
        assert False, "Not found in prototype list"

    new_tbl = []
    for name, prototypes in data.items():
        if prototypes is None:
            continue
        for p in prototypes:
            proto_name = _get_proto_name_only(p)
            d = {"proto_name": proto_name, "proto": p, "filename": name}
            new_tbl.append(d)

    return new_tbl


def _save_table_to_csv(table: List[Dict[str, str]], output_csv: str) -> None:
    """Save table to csv and pkl

    Parameters
    ----------
    table : List[Dict[str, str]]
        table data
    output_csv : str
        output csv file path
    """

    print(f"Saving table to csv file: {output_csv}")

    # convert new_tbl to pandas dataframe
    df = pd.DataFrame(table)

    # save df to csv
    df.to_csv(output_csv, index=False)


def main() -> None:
    """Main function"""
    args = _get_args()
    raw_input = _load_raw_input(args.raw_input)
    func_proto = _load_proto(args.proto)

    output_yml = (
        os.path.join(args.output_dir, args.output_yml)
        if args.output_yml is not None
        else None
    )
    output_csv = os.path.join(args.output_dir, args.output_csv)

    filtered_prototypes = _filter_prototypes(raw_input, func_proto)

    if output_yml:
        _save_dict_to_yml(filtered_prototypes, output_yml)

    proto_tbl = _prepare_table_with_func_prototype(filtered_prototypes, func_proto)

    _save_table_to_csv(proto_tbl, output_csv)


if __name__ == "__main__":
    main()
