"""
This entire file is simply a set of examples. The most basic is to
simply create a custom server by inheriting tserver.ThreadedServer
as shown below in MyServer.
"""

import jsocket
import logging

logger = logging.getLogger("jsocket.example_servers")

if __name__ == "__main__":
	import time
	import jsocket

	time.sleep(1)
	cPids = []
	for i in range(10):
		client = jsocket.JsonClient(address='127.0.0.1', port=5490)
		cPids.append(client)
		client.connect()
		client.send_obj({"message": "new connection"})
		client.send_obj({"message": i })
                obj = client.read_obj()
                print obj

	time.sleep(2)

	#for c in cPids:
	#	c.close()
