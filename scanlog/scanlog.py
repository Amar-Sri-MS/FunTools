#!/usr/bin/env python3

"""
This script will combine information from different parts to create a set of fast
traces that are used in the DV storage path. These traces are not lossy and very
fast to generate during run time. This script post-processes all of the separate
information into a human readable set of log entries.

This python script/utility takes in the following inputs:
1) fast trace files (generated from dpcsh command(s) for each LBA in the volume
sdebug {"class":"volume", "opcode" : "VOL_GET_TRACE_DATA", "params": {"slba":0}}
2) either f1 or f1-posix binaries

and returns a time-ordered list of human readable traces.
"""

import argparse
import textwrap
import os
import json
import sys
import subprocess
import re


def process_input_args(debug: bool=False) -> dict:
    if debug:
        print('process_input_args')

    description = """
    DV (Durable Volume) scanlog utility scans and post-processes fast tracing.

    This utility script will perform this work whether it is on a simulator or
    real hardware with different argument requirements.

    There two main modes of operation:
    1) utilizing the f1-posix binary (simulator)
    2) utilizing the f1       binary (real hardware)

    For both options you need the -f, -b, and -t options.

    For the f1/real hardware binary you need to specify the -o option.
    """
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--funos-path', '-f', action='store', type=str,
                        help='absolute path to [F]unOS/ for which your build is based', default=None)
    parser.add_argument('--objdump-file', '-o', action='store', type=str, 
                        help=textwrap.dedent('''\
                        [o]bjdump file (absolute path) to mips64-unknown-elf-objdump.
                        This is needed for real hardware analysis only.
                        EX: /Users/Shared/cross/mips64/bin/mips64-unknown-elf-objdump'''), default=None)
    parser.add_argument('--bin-type', '-b', action='store', type=str,
                        help='binary type- [p]osix or [h]ardware. Defaults to [p]osix', default='p')
    parser.add_argument('--trace-files', '-t', action='store',
                        help='absolute path to [t]race files', default=None)

    return parser.parse_args()

class AtomTable:
    """
    This class encapsulates all logic and memory storage of all the atom information found within
    the binary file. This is used to correlate a unique atom number (per trace in C code) to the
    file, line number, and string format of the trace

    funos_path      - absolute path to FunOS. Needed to find the f1 or f1-posix binary
    obj_dump_file   - absolute path to the mips64-unknown-elf-objdump for when the f1 binary
                      option is specified. Needed to get the atom table information out of
                      the f1 binary
    bin_type        - type of binary. Either posix or real hardware
    posix_bin_re    - regular expression to use when searching for the posix binary
    hardware_bin_re - regular expression to use when searching for the hardware binary
    bin_re          - binary regular expression used after considering the bin_type in
                      the generic file search method
    binary_file     - full pathed binary file found after the search (hopefully)
    atom_dict       - dict of dicts. Key'd on the message_id / atom number and hashes
                      to a dict containing the file_line and trace format info
    at_file_line    - dict key file_line string identifier
    at_trace        - dict key trace format string identifier
    """
    debug           : bool
    funos_path      : str
    obj_dump_file   : str
    bin_type        : str
    posix_bin_re    : str
    hardware_bin_re : str
    bin_re          : str
    binary_file     : str
    atom_dict       : dict
    at_file_line    : str
    at_trace        : str


    def __init__(self,
                 bin_type      : str=None,
                 funos_path    : str=None,
                 obj_dump_file : str=None,
                 debug         : bool=False):
        self.debug = debug

        self.posix_bin_re    = 'funos-f1-posix'
        self.hardware_bin_re = 'funos-f1'
        self.funos_path      = funos_path
        self.obj_dump_file   = obj_dump_file

        self.bin_type = bin_type
        if self.bin_type in ['p', 'posix']:
            self.bin_re = self.posix_bin_re
        elif self.bin_type in ['h', 'hardware']:
            self.bin_re = self.hardware_bin_re

            # sanity check for passed in arguments
            if not os.path.isfile(self.obj_dump_file):
                sys.exit(f'obj_dump_file:{self.obj_dump_file} does not exist')
        else:
            sys.exit(f'unexpected binary type argument bin_type:{self.bin_type}')

        self.binary_file    = None
        self.atom_dict      = {}
        self.at_file_line   = 'at_file_line'
        self.at_trace       = 'at_trace'

        # sanity check for passed in arguments
        if not os.path.exists(self.funos_path):
            sys.exit(f'funos_path:{self.funos_path} does not exist')

        self.find_binary_file()

    def find_binary_file(self) -> None:
        if self.debug:
            print(f'=== atom: find_binary_file')

        # traverse through all the sub-directories from pwd looking for the binary
        for root, dirs, files in os.walk(self.funos_path):
            for file in files:
                full_file_path = root + '/' + file

                # match is non-NULL if full match is found
                match = re.fullmatch(self.bin_re, file)

                # weed out non-executable files with same name
                if (match is not None) and os.access(full_file_path, os.X_OK):
                    if self.binary_file is None:
                        self.binary_file = full_file_path
                    else:
                        sys.exit(f'multiple binaries'
                             f'found:{self.binary_file} and {file}')

        # check to make sure we found the binary
        if self.binary_file is None:
            sys.exit(f'unable to find binary file named:{self.bin_re}')

    def process_atom_info(self) -> None:
        if self.debug:
            print(f'=== atom: process_atom_info')

        if self.bin_type in ['p', 'posix']:
            self.process_f1_posix_atom_info()
        elif self.bin_type in ['h', 'hardware']:
            self.process_f1_atom_info()
        else:
            sys.exit(f'unknown binary type argument bin_type:{self.bin_type}')

    def process_f1_posix_atom_info(self) -> None:
        if self.debug:
            print(f'=== atom: process_f1_posix_atom_info')

        # execute binary file with appropriate args to get out the atom info
        cmd = [self.binary_file, '--string-atom-dump-and-exit']

        try:
            byte_data = subprocess.check_output(cmd, shell=False)
        except subprocess.CalledProcessError as e:
            sys.exit(e.output)

        # convert from string to a list separating out on literal \n
        output_str  = byte_data.decode('utf-8').strip() # convert from bytes to string
        output_list = output_str.split('\n')            # split out string on newlines

        # delete the first list entry as it is just the command arg listing
        del output_list[0]

        atom_re = '\[.*\] *atom ([0-9]*) -> \"(.*\.c:[0-9]*) - (.*)\"'
        self.convert_atom_info_to_dict(output_list, atom_re)

    def process_f1_atom_info(self) -> None:
        if self.debug:
            print(f'=== atom: process_f1_atom_info')

        # execute binary file with appropriate args to get out the atom info
        cmd = [f'{self.funos_path}/makefiles/patch_wuid.py',
            '--objdump', self.obj_dump_file,
            '--dump-string-atoms',
            self.binary_file]

        try:
            byte_data = subprocess.check_output(cmd, shell=False)
        except subprocess.CalledProcessError as e:
            sys.exit(e.output)

        # convert from string to a list separating out on literal \n
        output_str  = byte_data.decode('utf-8').strip() # convert from bytes to string
        output_list = output_str.split('\n')            # split out string on newlines

        atom_re = '^atom ([0-9]*) -> \"(.*\.c:[0-9]*) - (.*)\"'
        self.convert_atom_info_to_dict(output_list, atom_re)

    def convert_atom_info_to_dict(self, output_list: list, atom_re: str) -> None:
        # process the list to generate a dict
        for item in output_list:
            search = re.search(atom_re, item)

            # check if the search was successful
            if search is not None:
                atom_num = int(search.group(1))

                # make sure this dict key has not yet been set. That should not
                # happen given the nature of how the underlying atom C code works
                if self.atom_dict.get(atom_num) == None:
                    atom_dict_entry = {self.at_file_line : search.group(2),
                                       self.at_trace     : search.group(3)}

                    self.atom_dict[atom_num] = atom_dict_entry

                    if self.debug:
                        print(f'dict:{self.atom_dict}')
                else:
                    sys.exit(f'ERROR - duplicate entry found for atom_num:{atom_num}.'
                         f'existing entry:{self.atom_dict[atom_num]}.'
                         f'new      entry:{atom_dict_entry}.')
            else:
                sys.exit(f'ERROR - atom entry:{item} does not match the expected regular'
                     f'expression:{atom_re}')

    def get_file_line(self, atom_num: int=None) -> int:
        if atom_num is not None:
            if self.atom_dict.get(atom_num) is not None:
                return self.atom_dict[atom_num][self.at_file_line]
            else:
                sys.exit(f'ERROR - atom_num:{atom_num} is not a valid key')
        else:
            sys.exit(f'ERROR - atom_num:{atom_num} not specified')

    def get_trace_fmt(self, atom_num: int=None) -> int:
        if atom_num is not None:
            if self.atom_dict.get(atom_num) is not None:
                return self.atom_dict[atom_num][self.at_trace]
            else:
                sys.exit(f'ERROR - atom_num:{atom_num} is not a valid key')
        else:
            sys.exit(f'ERROR - atom_num:{atom_num} not specified')

class FastTracing:
    """
    This class encapsulates all the logic to process the fast storage trace information that
    is generated by the C code. This corresponds to the information generated by the 
    storage/include/tracing.h and storage/common/tracing.c modules.

    This class will also munge together the information from these modules as well as the 
    info from the AtomTable class to create a complete trace entry that is sorted based on
    the timestamp

    trace_file_path     - absolute path to the location of the trace files generated from the
                          dpcsh command to get the fast traces
    fast_trace_file_re  - defines the file name regular expression to find/match when searching
                          for fast trace files
    record_size         - each FTR entry is 4 x 64-bit = 256 bits or 32 bytes. So a 'record' is
                          one FTR entry of 4 x 64-bit entries
    fast_trace_files    - list of all fast trace files found in find_trace_files()
    sorted_traces       - master list of all trace entries that is sorted on timestamp
    d_timestamp         - dict key timestamp string identifier
    d_trace_id          - dict key trace_id string identifier
    d_file_line         - dict key file_line string identifier
    d_trace_fmt         - dict key trace_format string identifier
    d_arg1              - dict key arg1 string identifier
    d_arg2              - dict key arg2 string identifier
    """
    debug              : bool
    trace_file_path    : str
    fast_trace_file_re : str
    record_size        : int
    fast_trace_files   : list
    sorted_traces      : list
    d_timestamp        : str
    d_trace_id         : str
    d_file_line        : str
    d_trace_fmt        : str
    d_arg1             : str
    d_arg2             : str

    def __init__(self,
                 trace_file_path : str,
                 debug           : bool=False):
        self.debug              = debug
        self.trace_file_path    = trace_file_path
        self.fast_trace_file_re = 'fast_trace_file'
        self.record_size        = 4
        self.fast_trace_files   = []
        self.sorted_traces      = []
        self.d_timestamp        = 'timestamp'
        self.d_trace_id         = 'trace_id'
        self.d_file_line        = 'file_line'
        self.d_trace_fmt        = 'trace_fmt'
        self.d_arg1             = 'arg1'
        self.d_arg2             = 'arg2'

        # sanity checks for passed in arguments
        if not os.path.exists(self.trace_file_path):
            sys.exit(f'trace_file_path:{self.trace_file_path} does not exist')

    def process_fast_tracing(self, at: AtomTable):
        if self.debug:
            print('\n=== process_fast_tracing')

        self.find_trace_files()

        for file in self.fast_trace_files:
            self.process_trace_file(at=at, file=file)

        self.sort_traces()

        self.output_traces()

    def find_trace_files(self):
        if self.debug:
            print('\n=== find_trace_files')
            print(f'trace_file_path:{self.trace_file_path}')
         
        # traverse through all the sub-directories from pwd looking for trace files
        for root, dirs, files in os.walk(self.trace_file_path):
            for file in files:

                # returns index of starting point match or -1 if no match
                found = file.find(self.fast_trace_file_re)
                if (found >= 0):
                    self.fast_trace_files.append(root + '/' + file)

        if self.debug:
            print(f'=== found {len(self.fast_trace_files)} trace files - {self.fast_trace_files}')

    def process_trace_file(self, at: AtomTable, file: str):
        if self.debug:
            print(f'\n=== processing {file}')

        with open(file, 'r') as f:
            data          = json.load(f)
            result_array = data['result']

            # check that result array contains records which are a fixed size
            if ((len(result_array) % self.record_size) != 0):
                sys.exit(f'ERROR - length of result_array:{len(result_array)} is '
                         f'not evenly divisible by record_size:{self.record_size}')

            """
            Each file contains the output of traces for a given lba. Each lba represents a 
            full FTR buffer. Each FTR buffer uses the first two records for identification
            so skip those. It also appears that the last entry is also not used (encoded 
            to 0 values)
            """
            start = self.record_size * 2
            stop  = len(result_array) - self.record_size
            step  = self.record_size
            for record_ix in range(start, stop, step):
                timestamp         = self.get_trace_timestamp(result_array, record_ix)
                trace_id          = self.get_trace_id(result_array, record_ix)
                module_id         = hex(self.get_trace_id_module_id(trace_id))
                trace_path_bitmap = hex(self.get_trace_id_trace_path_bitmap(trace_id))
                instance          = hex(self.get_trace_id_instance(trace_id))
                message_id        = hex(self.get_trace_id_message_id(trace_id))
                arg1              = self.get_trace_arg1(result_array, record_ix)
                arg2              = self.get_trace_arg2(result_array, record_ix)
                atom_num          = self.get_trace_id_message_id(trace_id)

                if self.debug:
                    print(f'record[{int(record_ix / self.record_size)}]')

                    print(f'   ix:{record_ix} - timestamp:{timestamp} trace_id:{hex(trace_id)} '
                          f'atom_num:{atom_num} module_id:{module_id} trace_path_bitmap:{trace_path_bitmap} '
                          f'instance:{instance} message_id:{message_id} arg1:{arg1} arg2:{arg2}')

                # create a dict for the trace information to be added to the sorted_traces list
                trace_dict = {self.d_timestamp : timestamp,
                              self.d_trace_id  : trace_id,
                              self.d_file_line : at.get_file_line(atom_num),
                              self.d_trace_fmt : at.get_trace_fmt(atom_num),
                              self.d_arg1      : arg1,
                              self.d_arg2      : arg2}

                self.sorted_traces.append(trace_dict)

    def sort_traces(self):
        if self.debug:
            print('\n=== sort traces')

        if self.debug:
            print('BEFORE')
            self.print_traces(self.sorted_traces)

        self.sorted_traces.sort(key=lambda i: i['timestamp'])

        if self.debug:
            print('AFTER')
            self.print_traces(self.sorted_traces)

    def print_traces(self, trace_list: list):
        for d in trace_list:
            print(f'{d}')

    def output_traces(self):
        if self.debug:
            print(f'\n=== output traces')

        for trace in self.sorted_traces:
            trace_id  = trace[self.d_trace_id]
            fmt_line  = trace[self.d_trace_fmt] % (trace[self.d_arg1], trace[self.d_arg2])
            timestamp = str(trace[self.d_timestamp] / 100000000).ljust(18,'0')
            cluster   = self.get_trace_id_vp_num(trace_id)
            core      = self.get_trace_id_core(trace_id)
            vp        = self.get_trace_id_vp_num(trace_id)
            file_line = trace[self.d_file_line]

            print(f'[{timestamp} {cluster}.{core}.{vp}] - {trace[self.d_file_line]} - {fmt_line}')


    """
    FTR entry definition (all entries are 64-bit in size):
    1) timestamp in nano-seconds
    2) trace_id
    3) trace arg1
    3) trace arg2

    trace_id layout - FunOS/storage/include/tracing.h

    uint64_t module_id:8;           // each client can have it's own module id.
    uint64_t trace_path_bitmap:8;   // each bit is a flag for the module's own
    uint64_t instance:8;
    uint64_t message_id:16;         // module scope message ids.
    uint64_t vp_num:8;              // vp where the trace originated
    uint64_t core:4;                // core
    uint64_t cluster:4;             // cluster
    uint64_t filler:8;              // spare

    """
    def get_trace_id(self, result_array: list, record_ix: int) -> int:
        trace_id_ix = record_ix + 1
        return result_array[trace_id_ix]

    def get_trace_timestamp(self, result_array: list, record_ix: int) -> int:
        timestamp_ix = record_ix
        return result_array[timestamp_ix]
        
    def get_trace_id_module_id(self, trace_id: int) -> int:
        return (trace_id & 0xFF)

    def get_trace_id_trace_path_bitmap(self, trace_id: int) -> int:
        return ((trace_id & 0xFF00) >> 8)

    def get_trace_id_instance(self, trace_id: int) -> int:
        return ((trace_id & 0xFF0000) >> 16)

    def get_trace_id_message_id(self, trace_id: int) -> int:
        return ((trace_id & 0xFFFF000000) >> 24)

    def get_trace_id_vp_num(self, trace_id: int) -> int:
        return ((trace_id & 0xFF0000000000) >> 40)

    def get_trace_id_core(self, trace_id: int) -> int:
        return ((trace_id & 0xF000000000000) >> 48)

    def get_trace_id_cluster(self, trace_id: int) -> int:
        return ((trace_id & 0xF0000000000000) >> 52)

    def get_trace_arg1(self, result_array: list, record_ix: int) -> int:
        arg1_ix = record_ix + 2
        return result_array[arg1_ix]

    def get_trace_arg2(self, result_array: list, record_ix: int) -> int:
        arg2_ix = record_ix + 3
        return result_array[arg2_ix]

    
def main():
    debug       = False
    input_args  = process_input_args(debug=debug)
    at          = AtomTable(debug         = debug,
                            bin_type      = input_args.bin_type,
                            funos_path    = input_args.funos_path,
                            obj_dump_file = input_args.objdump_file)

    # read in and process the atom information
    at.process_atom_info()
        
    if input_args.trace_files:
        ft = FastTracing(trace_file_path=input_args.trace_files, debug=debug)

        ft.process_fast_tracing(at)


# if this script is being called from the command line execute main. Otherwise if
# it is being called as a library from another script do not execute main
if __name__ == "__main__":
    main()
