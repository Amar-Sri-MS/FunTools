#!/bin/bash

# fail early
set -e

# move to source directory
cd ~/src/i2c_dbg

# build all the different platforms
make MACHINE=fs-bmc-hf ARTIFACTS_DIR=~/artifacts/fs-bmc-hf artifact 
