#!/usr/bin/env python2.7
"""Usage: dpc_restful_bench.py [-h] [--iterations=<N>]
          [--url=<string>]

Benchmarks restful DPC with given number of iterations.
"""

from __future__ import print_function
from docopt import docopt
import sys
import time
import requests

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
  for i in range(1, n_iterations + 1):
    requests.get(url)

  print("Total time: " + str(time.time() - start_time) + " secs. for " + str(n_iterations) + " iterations")

if (__name__ == "__main__"):
    main()
