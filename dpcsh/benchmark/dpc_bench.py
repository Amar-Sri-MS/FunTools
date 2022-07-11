#!/usr/bin/env python3
"""Usage: dpc_bench.py [-h] [--iterations=<N>] [--unix_socket=<file>]
          [--tcp_port=<port>] [--tcp_host=<host>]

Benchmarks DPC-echo with given number of iterations.
"""


from docopt import docopt
import sys
import time
import json
from dpc_client import DpcClient

def main():
  arguments = docopt(__doc__)
  if arguments['--tcp_port'] is None and arguments['--unix_socket'] is None:
    print('tcp_port or unix_socket is required')
    print(__doc__)
    sys.exit(1)

  n_iterations = int(arguments['--iterations']) if arguments['--iterations'] is not None else 1
  print("Starting the script")

  if arguments['--tcp_port'] is None:
    print('Running on Unix Socket', arguments['--unix_socket'])
    client = DpcClient(server_address=arguments['--unix_socket'], unix_sock=True)
  else:
    print('Running on TCP ', arguments['--tcp_host'], arguments['--tcp_port'])
    client = DpcClient(server_address=(arguments['--tcp_host'], int(arguments['--tcp_port'])))

  print("Connected")

  start_time = time.time()
  for _ in range(1, n_iterations + 1):
    ob = client.execute('echo', [
          {
              "class": "volume", 
              "opcode": "VOL_ADMIN_OPCODE_CREATE", 
              "params": {
                  "block_size": 4096, 
                  "capacity": 8589934592, 
                  "group_id": 1, 
                  "name": "test1", 
                  "type": "VOL_TYPE_BLK_LOCAL_THIN", 
                  "uuid": "a8c6820a8b0b3ef1"
              }
          }
      ], None)
    print(len(json.dumps(ob)))

  print("Total time: " + str(time.time() - start_time) + " secs. for " + str(n_iterations) + " iterations")

if (__name__ == "__main__"):
    main()
