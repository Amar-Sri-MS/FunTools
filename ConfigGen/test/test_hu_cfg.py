#!/usr/bin/env python2.7

import collections
import json

from pprint import pprint
import glob, os, sys, re, datetime
import getopt, platform, tempfile
import logging, sys

""" Test file that parse combined json file and print out
hu config, and used for for comparing the output from c file using
generated c,h struct
"""

# Add quotes to keys, hex values, remove comments and remove trailing commas
def standardize_json(in_cfg, out_cfg):
    with open(in_cfg, 'r') as fh:
        fixed_json = fh.read()

        logging.debug("Removing Comments in %s"% (in_cfg))
        fixed_json = remove_comments(fixed_json)

        logging.debug("Add quotes to keys in %s"% (in_cfg))
        #Match for the text before ":"(i.e. dict key) and add quotes if it does not have them already
        fixed_json = re.sub( r'\n(\s*)(?!")(\S+)\s*:', r'\n\1"\2":', fixed_json)

        logging.debug("Convert non-quoted hex values to decimals in %s"% (in_cfg))
        #Match for the non-quoted hex values in dict(Hex prefix is "0x") and replace with equivalent decimal values
        fixed_json = re.sub( r'[^"]0x([a-fA-F0-9]+)(,?|$)', lambda m: lambda_hextoint(m.groups()), fixed_json)

        logging.debug("Strip empty lines and trailing spaces in %s"% (in_cfg))
        #Remove empty lines(even if they have any kind of white spaces) and trailing white spaces
        fixed_json = os.linesep.join([s.rstrip() for s in fixed_json.splitlines() if s.strip()])

        logging.debug("Strip trailing commas in %s"% (in_cfg))
        fixed_json = remove_trailing_commas(fixed_json)

        f = open("%s" % out_cfg, 'w')
        f.write(fixed_json)
        f.close()

def lambda_hextoint(x):
    return str(int(x[0], 16))+x[1]

#Remove comments in json file
def remove_comments(json_like):
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
def remove_trailing_commas(json_like):
    """
    Removes trailing commas from *json_like* and returns the result.  Example::
        >>> remove_trailing_commas('{"foo":"bar","baz":["blah",],}')
        '{"foo":"bar","baz":["blah"]}'
    """
    pos = 0
    while pos < len(json_like):
        if json_like[pos] == '"':
            pos = consume_string(json_like, pos)
            assert json_like[pos-1] == '"'
        elif json_like[pos] in "]}":
            prev = pos-1
            assert prev >= 0
            while json_like[prev].isspace():
                prev -= 1
                assert prev >= 0
            if json_like[prev] == ",":
                json_like = json_like[:prev] + json_like[pos:]
                assert json_like[prev] in "]}"
                pos = prev + 1
            else:
                pos += 1
        else:
            pos += 1
    return json_like

def consume_string(json_like, pos):
    assert json_like[pos] == '"'
    pos += 1
    while json_like[pos] != '"':
        c = json_like[pos]
        if c == "\\":
            pos += 2
        else:
            pos += 1
    return pos + 1

def print_HostUnits(HostUnits):
    print "HostUnits: 0x%x" % HostUnits["hu_en"]
    print ""

def print_HostUnit(HostUnit):
    for i, l in enumerate(HostUnit):
        index = l["_args"]
    	if index == ['all']:
    		continue
        ctl_en = l["ctl_en"]
        print "HostUnit[%d].ctl_en: 0x%x" % (index[0], ctl_en)

    print ""

def load_cfg(cfgfile):
    # read the file
    try:
        f = tempfile.NamedTemporaryFile(mode="r")
        standardize_json(cfgfile, f.name)
        cfg = json.load(f)
    except Exception as e:
        logging.error("error: %s", e)
        RuntimeError("Error loading and parsing projectdb %s" % cfgfile)
        raise e

    HostUnits = cfg.get("HostUnits")
    HostUnit = cfg.get("HostUnit")

    print_HostUnits(HostUnits)
    print_HostUnit(HostUnit)
    #pprint(HostUnits)
    #pprint(HostUnit)


def Usage():
    sys.stderr.write('test_hu_cfg.py: usage: [-c json cfg output file]')

def main():

    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    print("test hu_cfg")
    print("")

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hc:')

    except getopt.GetoptError as err:
        print str(err)
        Usage()
        sys.exit(2)

    for o, a in opts:
        if o in ('-h', '--help'):
            Usage()
            sys.exit(1)
        elif o in ('-c', '--cfgfile'):
            cfgfile = a
            logging.debug("cfg file: %s", a)
        else:
            assert False, 'Unhandled option %s' % o

    load_cfg(cfgfile)

if __name__ == "__main__":
    main()