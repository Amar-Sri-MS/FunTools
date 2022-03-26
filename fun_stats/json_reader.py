#
#  CFG_reader.py
#
#  Reads json config files, standrdize them and creates json object
#
#  Created by Nag Ponugoti on 2018-03-28
#
#  Copyright  2018 Fungible Inc. All rights reserved.
#
import collections
import copy
import glob
import os
import pdb
import re
import json
import getopt, tempfile
import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def ordered_load(stream):
    return json.load(stream,  object_pairs_hook=collections.OrderedDict)

# Reads the config files from input directory and creates standardized json object
class CFG_Reader(object):
    def __init__(self, dirname):
        self.__read_dir(dirname)

    def __read_dir(self, dirname):
        self.cfg = collections.OrderedDict()
        for cfg_file in glob.glob(os.path.join(dirname, '*.cfg')):
            f_name = os.path.splitext(os.path.basename(cfg_file))[0]
            log.info("Processing config file: {}".format(f_name))
            json_stream = self.__read_file(cfg_file)
            self.cfg[f_name.lower()] = json_stream

    def __read_file(self, f_name):
        json_stream = None
        p = JSON_Reader()
        json_stream = p.read_file(f_name)
        assert json_stream != None, "JSON Load issues for file: {}".format(f_name)
        return json_stream

    def get(self):
        return self.cfg

    def __str__(self):
        r_str = ""
        for key, val in self.cfg.items():
            r_str += "{}:\n{}".format(key, val)
        return r_str
    __repr__ = __str__

    # Merge two dictionaries
    def merge_dicts(self, cfg, cfg_new):
        merged_cfg = cfg
        for key in list(cfg_new.keys()):
            if key in list(merged_cfg.keys()):
                merged_cfg[key].update(cfg_new[key])
            else:
                merged_cfg[key] = cfg_new[key]
        return merged_cfg

class JSON_Reader(object):
    def __init__(self):
        pass

    # Add quotes to keys, hex values, remove comments and remove trailing commas
    def standardize_json(self, in_cfg, out_cfg):
        with open(in_cfg, 'r') as fh:
            fixed_json = ''.join(line for line in fh)
            log.debug("Removing Comments in %s"% (in_cfg))
            fixed_json = self.remove_comments(fixed_json)

            log.debug("Add quotes to keys in %s"% (in_cfg))
            #Match for the text before ":"(i.e. dict key) and add quotes if it does not have them already
            fixed_json = re.sub( r'\n(\s*)(?!")(\S+)\s*:', r'\n\1"\2":', fixed_json)

            log.debug("Convert non-quoted hex values to decimals in %s"%
                      (in_cfg))
            #Match for the non-quoted hex values in dict(Hex prefix is "0x") and replace with equivalent decimal values
            fixed_json = re.sub( r'[^"]0x([a-fA-F0-9]+)(,?|$)', lambda m: self.lambda_hextoint(m.groups()), fixed_json)

            log.debug("Strip empty lines and trailing spaces in %s"% (in_cfg))
            #Remove empty lines(even if they have any kind of white spaces) and trailing white spaces
            #fixed_json = os.linesep.join([s.rstrip() for s in fixed_json.splitlines() if s.strip()])

            log.debug("Strip trailing commas in %s"% (in_cfg))
            fixed_json = self.remove_trailing_commas(fixed_json)

            f = open("%s" % out_cfg, 'w')
            f.write(fixed_json)
            f.close()

    def lambda_hextoint(self, x):
            return str(int(x[0], 16))+x[1]

    #Remove comments in json file
    def remove_comments(self, json_like):
        comments_re = re.compile(
                r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
                re.DOTALL | re.MULTILINE
        )
        def replacer(match):
            s = match.group(0)
            if s[0] == '/':
                return "\r"
            return s
        return comments_re.sub(replacer, json_like)


    #Remove trailing commas in json file
    def remove_trailing_commas(self, json_like):
        """
        Removes trailing commas from *json_like* and returns the result.  Example::
            >>> remove_trailing_commas('{"foo":"bar","baz":["blah",],}')
            '{"foo":"bar","baz":["blah"]}'
        """
        pos = 0
        while pos < len(json_like):
            if json_like[pos] == '"':
                pos = self.consume_string(json_like, pos)
                assert json_like[pos-1] == '"'
            elif json_like[pos] in "]}":
                prev = pos-1
                assert prev >= 0
                while json_like[prev].isspace():
                    prev -= 1
                    assert prev >= 0
                if json_like[prev] == ",":
                    json_like = json_like[:prev]+ " "+ json_like[prev+1:]
                pos += 1
            else:
                pos += 1
        return json_like
    def consume_string(self, json_like, pos):
        assert json_like[pos] == '"'
        pos += 1
        while json_like[pos] != '"':
            c = json_like[pos]
            if c == "\\":
                pos += 2
            else:
                pos += 1
        return pos + 1

    def read_file(self, f_name):
        log.debug("handling config for %s" % f_name)
        json_stream = None
        t_file = tempfile.NamedTemporaryFile(mode="r")
        self.standardize_json(f_name, t_file.name)
        json_stream = ordered_load(t_file)
        return json_stream

