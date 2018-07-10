##
#
# This entire file is simply a set of examples. The most basic is to
# simply create a custom server by inheriting tserver.ThreadedServer
# as shown below in MyServer.
#

import jsocket
import logging

logger = logging.getLogger("jsocket.example_servers")

client = None
if __name__ == "__main__":
        import time
        import jsocket

        cPids = []
        for i in range(10):
                global client
                client = jsocket.JsonClient()
                cPids.append(client)
                client.connect()
                client.send_obj({"message": "****NAG****"})
                client.send_obj({"message": i })
                for x in range(2):
                   print client.read_obj()

        time.sleep(10)
