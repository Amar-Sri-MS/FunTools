# Problems to be solved
This fold provides a python based PTF server process. It listens and accepts socket connections from clients. From the connected socket, the server receives testing instructions and raw packets in JSON format, then it would use PTF framework to inject raw packets to UUT and return received packets back from selected ports to the client. This server manages port mapping with UUT via intf_map.json.

# File structures
* Makefile : Use " make venv" to set up python virtual env, which would prepare PTF needed python modules.
* Pipfile : provide python dependencies for python virtual env.
* README : this file
* intf_map.json : providing UUT port name to PTF port number mapping
* ptf_test.py : Main server codes
* start_ptf_svr.py : a wrapper script to start ptf server.
* util.py : Util functions
* client.py : testing client
* start_client.py: a wrapper script to start client test
* ptf_svr_test.json : provide testing data to client.py

# Message format
## Request Message
Request message is in  JSON format. It takes following properties
1. in_intf : Input PTF port
2. out_intfs : Outgoing PTF ports array
3. pkt : Raw packet

```
{ "in_intf" : 0, "out_intf": [1], "data" : "00 DE AD BE EF 00 FE DC BA 44 55 77 08 00 45 00 00 BA 00 69 00 00 40 06 62 D2 01 01 01 01 14 01 01 01 04 D2 00 50 00 00 00 00 00 00 00 00 50 02 20 00 D6 45 00 00 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F 20 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F 30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D 3E 3F 40 41 42 43 44 45 46 47 48 49 4A 4B 4C 4D 4E 4F 50 51 52 53 54 55 56 57 58 59 5A 5B 5C 5D 5E 5F 60 61 62 63 64 65 66 67 68 69 6A 6B 6C 6D 6E 6F 70 71 72 73 74 75 76 77 78 79 7A 7B 7C 7D 7E 7F 80 81 82 83 84 85 86 87 88 89 8A 8B 8C 8D 8E 8F 90 91"}
```

## Response Message
Response message is in JSON format. It has following properties.
1. message : Message from server side
2. error : True / False, True means server hits some error condition and doesn't get response packets
3. pkt : Response packet from UUT
```
{u'message': u'Successfuled get packet at port 1', u'pkt': u'FE DC BA 44 55 77 00 DE AD BE EF 00 08 00 45 00 00 BA 00 69 00 00 3F 06 63 D2 01 01 01 01 14 01 01 01 04 D2 00 50 00 00 00 00 00 00 00 00 50 02 20 00 D6 45 00 00 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F 20 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F 30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D 3E 3F 40 41 42 43 44 45 46 47 48 49 4A 4B 4C 4D 4E 4F 50 51 52 53 54 55 56 57 58 59 5A 5B 5C 5D 5E 5F 60 61 62 63 64 65 66 67 68 69 6A 6B 6C 6D 6E 6F 70 71 72 73 74 75 76 77 78 79 7A 7B 7C 7D 7E 7F 80 81 82 83 84 85 86 87 88 89 8A 8B 8C 8D 8E 8F 90 91', u'error': u'False'}
```

# How to use
1. Update intf_map.json to provide needed UUT port name to PTF port # mapping.
2. Use start_ptf_svr.py to start ptf server. The server listen on 9000 port
3. Use "start_client.py" to send request to server and get response back. Following is the testing output from client.py
4. Running logs could be found at logs/ directory.

```
Sending packet fpg 0 -> fpg 1 (1.1.1.1 -> 20.1.1.1)
Sending JSON Request : { "in_intf" : 0, "out_intf": [1], "data" : "00 DE AD BE EF 00 FE DC BA 44 55 77 08 00 45 00 00 BA 00 69 00 00 40 06 62 D2 01 01 01 01 14 01 01 01 04 D2 00 50 00 00 00 00 00 00 00 00 50 02 20 00 D6 45 00 00 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F 20 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F 30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D 3E 3F 40 41 42 43 44 45 46 47 48 49 4A 4B 4C 4D 4E 4F 50 51 52 53 54 55 56 57 58 59 5A 5B 5C 5D 5E 5F 60 61 62 63 64 65 66 67 68 69 6A 6B 6C 6D 6E 6F 70 71 72 73 74 75 76 77 78 79 7A 7B 7C 7D 7E 7F 80 81 82 83 84 85 86 87 88 89 8A 8B 8C 8D 8E 8F 90 91"}
Receive JSON Response : {u'message': u'Successfuled get packet at port 1', u'pkt': u'FE DC BA 44 55 77 00 DE AD BE EF 00 08 00 45 00 00 BA 00 69 00 00 3F 06 63 D2 01 01 01 01 14 01 01 01 04 D2 00 50 00 00 00 00 00 00 00 00 50 02 20 00 D6 45 00 00 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F 20 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F 30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D 3E 3F 40 41 42 43 44 45 46 47 48 49 4A 4B 4C 4D 4E 4F 50 51 52 53 54 55 56 57 58 59 5A 5B 5C 5D 5E 5F 60 61 62 63 64 65 66 67 68 69 6A 6B 6C 6D 6E 6F 70 71 72 73 74 75 76 77 78 79 7A 7B 7C 7D 7E 7F 80 81 82 83 84 85 86 87 88 89 8A 8B 8C 8D 8E 8F 90 91', u'error': u'False'}
```
Server output is following
```
Receiving Pkt from Client :
 ###[ Ethernet ]### 
  dst       = 00:de:ad:be:ef:00
  src       = fe:dc:ba:44:55:77
  type      = 0x800
###[ IP ]### 
     version   = 4
     ihl       = 5
     tos       = 0x0
     len       = 186
     id        = 105
     flags     = 
     frag      = 0
     ttl       = 64
     proto     = 6
     chksum    = 0x62d2
     src       = 1.1.1.1
     dst       = 20.1.1.1
     \options   \
###[ TCP ]### 
        sport     = 1234
        dport     = 80
        seq       = 0
        ack       = 0
        dataofs   = 5
        reserved  = 0
        flags     = S
        window    = 8192
        chksum    = 0xd645
        urgptr    = 0
        options   = []
###[ Raw ]### 
           load      = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91'



Receive packets from PTF : 
###[ Ethernet ]### 
  dst       = 00:de:ad:be:ef:00
  src       = fe:dc:ba:44:55:77
  type      = 0x800
###[ IP ]### 
     version   = 4
     ihl       = 5
     tos       = 0x0
     len       = 186
     id        = 105
     flags     = 
     frag      = 0
     ttl       = 64
     proto     = 6
     chksum    = 0x62d2
     src       = 1.1.1.1
     dst       = 20.1.1.1
     \options   \
###[ TCP ]### 
        sport     = 1234
        dport     = 80
        seq       = 0
        ack       = 0
        dataofs   = 5
        reserved  = 0
        flags     = S
        window    = 8192
        chksum    = 0xd645
        urgptr    = 0
        options   = []
###[ Raw ]### 
           load      = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91'

```

