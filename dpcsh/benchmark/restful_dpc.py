#!/usr/bin/env python3
"""Usage: restful_dpc.py [-h] [--unix_socket=<file>] [--response-size=<bytes>]
          [--tcp_port=<port>] [--https]

Provides restful DPC-echo service via Flask.
"""

from docopt import docopt
import flask
from dpc_client import DpcClient
import json
import math
import sys
from gevent.pywsgi import WSGIServer

app = flask.Flask(__name__)
client = None
response_size = None

@app.route('/', methods=["GET", "POST"])
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
  s = json.dumps(result)
  return s * (int(response_size / len(s))) + s[:(response_size % len(s))]

def main():
  global client, response_size
  arguments = docopt(__doc__)
  if arguments['--tcp_port'] is None and arguments['--unix_socket'] is None:
    print('tcp_port or unix_socket is required')
    print(__doc__)
    sys.exit(1)

  response_size = 207 if arguments['--response-size'] is None else int(arguments['--response-size'])

  if arguments['--tcp_port'] is None:
    print('Running on Unix Socket', arguments['--unix_socket'])
    client = DpcClient(server_address=arguments['--unix_socket'], unix_sock=True)
  else:
    print('Running on TCP localhost:', arguments['--tcp_port'])
    client = DpcClient(server_address=('localhost', int(arguments['--tcp_port'])))

  print("Connected")

  if arguments['--https']:
    server = WSGIServer(
            ('0.0.0.0', 5000),
            app,
            log='default',
            keyfile='key.pem',
            certfile='cert.pem'
        )
    server.serve_forever()
  else:
    server = WSGIServer(
            ('0.0.0.0', 5000),
            app,
            log='default'
        )
    server.serve_forever()

if __name__ == "__main__":
    main()
