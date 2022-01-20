#!/usr/bin/env python2.7

# Converts lenient json to standard json
#The input files are allowed to make two side-steps from the standard JSON
#specification:
#   - Allow comments
#   - Allow hex values
# Both are intended to improve readability of the files, and leverage our
# own jsonutil (which has a lenient parser) to do the initial parsing.

import json
import re
import os
import logging
from itertools import chain

logger = logging.getLogger("jsonutils")
logger.setLevel(logging.INFO)

#Remove comments in json file
def _remove_comments(json_like):
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
def _remove_trailing_commas(json_like):
    """
    Removes trailing commas from *json_like* and returns the result.  Example::
        >>> _remove_trailing_commas('{"foo":"bar","baz":["blah",],}')
        '{"foo":"bar","baz":["blah"]}'
    """
    pos = 0
    while pos < len(json_like):
        if json_like[pos] == '"':
            pos = _consume_string(json_like, pos)
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

def _consume_string(json_like, pos):
    assert json_like[pos] == '"'
    pos += 1
    while json_like[pos] != '"':
        c = json_like[pos]
        if c == "\\":
            pos += 2
        else:
            pos += 1
    return pos + 1

def _lambda_hextoint(x):
    return str(int(x[0], 16))+x[1]

# Add quotes to keys, hex values, remove comments and remove trailing commas
def standardize_json(json):
    logger.debug('Removing Comments')
    json = _remove_comments(json)

    logger.debug("Add quotes to keys")
    #Match for the text before ":"(i.e. dict key) and add quotes if it does not have them already
    json = re.sub( r'\n(\s*)(?!")(\S+)\s*:', r'\n\1"\2":', json)

    logger.debug("Convert non-quoted hex values to decimals")
    #Match for the non-quoted hex values in dict(Hex prefix is "0x") and replace with equivalent decimal values
    json = re.sub( r'[^"]0x([a-fA-F0-9]+)(,?|$)', lambda m: _lambda_hextoint(m.groups()), json)

    logger.debug("Strip empty lines and trailing spaces")
    #Remove empty lines(even if they have any kind of white spaces) and trailing white spaces
    json = os.linesep.join([s.rstrip() for s in json.splitlines() if s.strip()])

    logger.debug("Strip trailing commas")
    json = _remove_trailing_commas(json)

    return json

#Groups the range strings
def _group_to_range(group):
    group = ''.join(group.split())
    sign, g = ('-', group[1:]) if group.startswith('-') else ('', group)
    r = g.split('-', 1)
    r[0] = sign + r[0]
    r = sorted(int(__) for __ in r)
    return list(range(r[0], 1 + r[-1]))

#Groups and expands range strings
def rangeexpand(comma_seperated_range_string):
    ranges = chain.from_iterable(_group_to_range(__) for __ in comma_seperated_range_string.split(','))
    return sorted(set(ranges))

# Merge two dictionaries
# If they have the same key, merge contents
def merge_dicts(cfg1, cfg2):
    new_cfg = cfg1
    for key in list(cfg2.keys()):
        logger.debug('Adding key: {}'.format(key))
        if key in list(new_cfg.keys()):
            new_cfg[key].update(cfg2[key])
        else:
            new_cfg[key] = cfg2[key]

    return new_cfg

# Merge two dictionaries
# Like merge_dicts above, but recursively merges dictionaries too
def merge_dicts_recursive(cfg1, cfg2):
    for k, v in cfg1.items():
        if isinstance(v, dict):
            merge_dicts_recursive(v, cfg2.setdefault(k, {}))
        elif isinstance(v, list) and k in cfg2:
            cfg2[k].extend(v)
        elif not k in cfg2:
            cfg2[k] = v

    return cfg2

# Raise an error when duplicate keys are found
# Otherwise the default loader silently loads the last value, which
#  can lead to subtle and hard to find errors
def _json_ordered_pair_handler(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
           raise ValueError("Duplicate key: {}".format(k))
        else:
           d[k] = v
    return d

# Load a Fungible-style json
# A Fungible-style json may contain C-style comments, unquoted values etc
def load_fungible_json(fname):
    with open(fname, 'r') as f:
        this_json = f.read()
        this_json = standardize_json(this_json)
        try:
            return json.loads(this_json, object_pairs_hook=_json_ordered_pair_handler)
        except ValueError as e:
            raise ValueError("Error processing {}:{}".format(fname, str(e)))

    return None
