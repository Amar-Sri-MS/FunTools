#!/usr/bin/env python3
"""Usage: dpc_restful_bench.py [-h] [--iterations=<N>]
          [--url=<string>] [--keep-alive] [--verbose]

Benchmarks restful DPC with given number of iterations.
"""

from docopt import docopt
import sys
import time
import requests
import logging

def main():
  arguments = docopt(__doc__)
  if arguments['--url'] is None:
    print('URL is required')
    print(__doc__)
    sys.exit(1)

  url = arguments['--url']
  n_iterations = int(arguments['--iterations']) if arguments['--iterations'] is not None else 1
  print("Starting the script")

  start_time = time.time()

  if arguments['--verbose']:
    logging.basicConfig(level=logging.DEBUG)

  if not arguments['--keep-alive']:
    for _ in range(1, n_iterations + 1):
      requests.get(url)
  else:
    print('Keep-alive')
    s = requests.session()
    for _ in range(1, n_iterations + 1):
      s.get(url, stream = False)

  print("Total time: " + str(time.time() - start_time) + " secs. for " + str(n_iterations) + " iterations")

if (__name__ == "__main__"):
    main()
