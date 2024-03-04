#!/bin/bash

# move to source directory
cd ~/src/i2c_dbg

# build all the different platforms
make MACHINE=fs-bmc-hf
make MACHINE=rpi
make MACHINE=qemu

# copy each build to artifacts drop
for p in build/* ; do
    i=`basename $p`
    mkdir ~/artifacts/$i
    cp build/$i/i2c_dbg.so ~/artifacts/$i
    cp bmc_sbp_chal.py libi2c.so ~/artifacts/$i
done
