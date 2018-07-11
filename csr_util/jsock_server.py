##
#
# This entire file is simply a set of examples. The most basic is to
# simply create a custom server by inheriting tserver.ThreadedServer
# as shown below in MyServer.
#

import jsocket
import logging

logger = logging.getLogger("jsocket.example_servers")

##
#       This is a basic example of a custom ThreadedServer.
class MyServer(jsocket.ThreadedServer):
        def __init__(self):
                super(MyServer, self).__init__()
                self.timeout = 2.0
                logger.warning("MyServer class in customServer is for example purposes only.")

        ##
        #  virtual method
        def _process_message(self, obj):
                if obj != '':
                        if obj['message'] == "new connection":
                                logger.info("new connection.")

##
#       This is an example factory thread, which the server factory will
#               instantiate for each new connection.
#
class MyFactoryThread(jsocket.ServerFactoryThread):
        def __init__(self):
                super(MyFactoryThread, self).__init__()
                self.timeout = 2.0

        ##
        #  virtual method - Implementer must define protocol
        def _process_message(self, obj):
                if obj != '':
                        if obj['message'] == "new connection":
                                logger.info("new connection.")
                        else:
                                logger.info(obj)
                        self.send_obj({"NAG": 1})
                        self.send_obj({"NAG": 2})

if __name__ == "__main__":
        import time
        import jsocket

        server = jsocket.ServerFactory(MyFactoryThread)
        server.timeout = 2.0
        server.start()

        #time.sleep(5)
        #server.stop()
        #server.join()
