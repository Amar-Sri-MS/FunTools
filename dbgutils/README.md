# HW debug utilities
This module provides following features:
* i2c raw csr/read api
* i2c relay tcp server which runs on the server to which i2c adapter is physically connected
  and accepts peek/poke requests in json format from the clients and call peek/poke api
  and returns the response in json.
* i2c json client.
* csr peek/poke/list/find utility api
* simple cli for hw folks to build debug utilities

## Other standalone utilities

These are pure debug utilties that can be useful to integrate later.
These are run as standlone python scripts and are not installed.

### bbv/getbbv.py

Python script that prints out histogram of basic block vector sizes
for any MIPS64 binary




# Install the dependancies
sudo python setup.py install

