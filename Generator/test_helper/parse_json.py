#!/usr/bin/env python3
#
# Parses file containing JSON provided on the command line.
# Succeeds if file parses correctly, fails if file is not valid JSON.

import json
import sys

def main():
  if len(sys.argv) != 2:
    sys.stderr.write('Usage: parse_json filename\n')
  try:
    f = open(sys.argv[1], 'r')
  except Exception as e:
    sys.stderr.write('Exception when opening file: %s' % e)
    sys.exit(1)


  try:
    json.load(f) 
  except Exception as e:
    sys.stderr.write('Exception when parsing JSON: %s' % e)
    sys.exit(1)

  # Worked!
  sys.exit(0)


if __name__ == '__main__':
  main()

