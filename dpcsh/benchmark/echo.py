#!/usr/bin/env python3
import socket
import json

HOST = 'localhost'
PORT = 44444

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print('Connected by', addr)
while True:
    f = conn.makefile()
    data = f.readline()
    if not data: break
    j = json.loads(data)
    conn.sendall(json.dumps({"result": "ok", "tid": j["tid"]}) + '\n')
conn.close()
