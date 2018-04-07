#
#  CFG_reader.py
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

def ordered_load(stream):
    return json.load(stream,  object_pairs_hook=collections.OrderedDict)

class CFG_Reader(object):
    def __init__(self, dirname):
        self.__read_dir(dirname)

    def __read_dir(self, dirname):
        self.cfg = collections.OrderedDict()
        for cfg_file in glob.glob(os.path.join(dirname, '*.cfg')):
            f_name = os.path.splitext(os.path.basename(cfg_file))[0]
            print f_name
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
        for key, val in self.cfg.iteritems():
            r_str += "{}:\n{}".format(key, val)
        return r_str
    __repr__ = __str__

    # Merge two dictionaries
    def merge_dicts(cfg, cfg_new):
            merged_cfg = cfg
            for key in cfg_new.keys():
                    print "Adding key: %s" % key
                    if key in merged_cfg.keys():
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
		    fixed_json = ''.join(line for line in fh if not line.startswith('//'))
		    print "Removing Comments in %s"% (in_cfg)
		    fixed_json = self.remove_comments(fixed_json)

		    print "Add quotes to keys in %s"% (in_cfg)
		    #Match for the text before ":"(i.e. dict key) and add quotes if it does not have them already
		    fixed_json = re.sub( r'\n(\s*)(?!")(\S+)\s*:', r'\n\1"\2":', fixed_json)

		    print "Convert non-quoted hex values to decimals in %s"% (in_cfg)
		    #Match for the non-quoted hex values in dict(Hex prefix is "0x") and replace with equivalent decimal values
		    fixed_json = re.sub( r'[^"]0x([a-fA-F0-9]+)(,?|$)', lambda m: self.lambda_hextoint(m.groups()), fixed_json)

		    print "Strip empty lines and trailing spaces in %s"% (in_cfg)
		    #Remove empty lines(even if they have any kind of white spaces) and trailing white spaces
		    #fixed_json = os.linesep.join([s.rstrip() for s in fixed_json.splitlines() if s.strip()])

		    print "Strip trailing commas in %s"% (in_cfg)
		    fixed_json = self.remove_trailing_commas(fixed_json)

		    f = open("%s" % out_cfg, 'w')
		    #print fixed_json
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
                    if s[0] == '/': return ""
                    return s
            return comments_re.sub(replacer, json_like)

    #Remove trailing commas in json file
    def remove_trailing_commas(self, json_like):
            """
            Removes trailing commas from *json_like* and returns the result.  Example::
                    >>> remove_trailing_commas('{"foo":"bar","baz":["blah",],}')
                    '{"foo":"bar","baz":["blah"]}'
            """
            trailing_object_commas_re = re.compile(
                    r'(,)\s*}(?=([^"\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"]*$)')
            trailing_array_commas_re = re.compile(
                    r'(,)\s*\](?=([^"\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"]*$)')
            # Fix objects {} first
            objects_fixed = trailing_object_commas_re.sub("}", json_like)
            # Now fix arrays/lists [] and return the result
            return trailing_array_commas_re.sub("]", objects_fixed)

    def read_file(self, f_name):
        print "handling module config %s" % f_name
        json_stream = None
        t_file = tempfile.NamedTemporaryFile(mode="r")
        print "working with temp file %s" % t_file.name
        self.standardize_json(f_name, t_file.name)
        json_stream = ordered_load(t_file)
        return json_stream


