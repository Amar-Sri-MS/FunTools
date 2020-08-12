#!/usr/bin/env python2.7
"""Usage: restful_dpc.py [-h] [--unix_socket=<file>]
          [--tcp_port=<port>]

Provides restful DPC-echo service via Flask.
"""

from __future__ import print_function
from docopt import docopt
import flask
from dpc_client import DpcClient
import json
import sys

app = flask.Flask(__name__)
client = None

@app.route('/', methods=["GET"])
def echo():
  global client
#  if not flask.request.json:
#    print("Bad json format")
#    flask.abort(400)

  result = client.execute('echo', [
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
  return json.dumps(result)

def main():
  global client
  arguments = docopt(__doc__)
  if arguments['--tcp_port'] is None and arguments['--unix_socket'] is None:
    print('tcp_port or unix_socket is required')
    print(__doc__)
    sys.exit(1)

  if arguments['--tcp_port'] is None:
    print('Running on Unix Socket', arguments['--unix_socket'])
    client = DpcClient(server_address=arguments['--unix_socket'], unix_sock=True)
  else:
    print('Running on TCP localhost:', arguments['--tcp_port'])
    client = DpcClient(server_address=('localhost', int(arguments['--tcp_port'])))

  print("Connected")

  app.run(host="0.0.0.0")

if __name__ == "__main__":
    main()