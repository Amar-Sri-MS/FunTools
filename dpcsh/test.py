#!/usr/bin/env python3

import socket
import time
import sys
import _thread

# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

def read_and_print():
	chunk = 1024
	buffer = sock.recv(chunk)
	buffering = True
	while buffering:
		if "\n" in buffer:
			(line, buffer) = buffer.split("\n", 1)
			print(line)
		else:
			more = sock.recv(chunk)
			if not more:
				buffering = False
			else:
				buffer += more
	if buffer:
		print(buffer)

# Connect the socket to the port where the server is listening
server_address = '/tmp/funos-dpc-text.sock'
print("connecting to '%s'" % server_address)

try:
    sock.connect(server_address)
except socket.error as msg:
    print(msg)
    sys.exit(1)

_thread.start_new_thread(read_and_print, ())

sock.sendall('echo "hello DPC!"\n')
sock.sendall("help\n")
sock.sendall("fibo 10\n")
#sock.sendall("setenv $foo {x: y}\n")
#sock.sendall("getenv $foo\n")
sock.sendall("garbage\n")
sock.sendall('echo "all done!"\n')

time.sleep(2) # important because otherwise the print thread dies too early
