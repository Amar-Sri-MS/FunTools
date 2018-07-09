#!/usr/bin/env python

import argcomplete, argparse

parser = argparse.ArgumentParser(prog='csr')
parser.add_argument('positional', choices=['spam', 'eggs'])
parser.add_argument('--optional', choices=['foo1', 'foo2', 'bar'])
argcomplete.autocomplete(parser)
args = parser.parse_args()

def main(**args):
  pass

if __name__ == '__main__':
  main(**vars(args))
