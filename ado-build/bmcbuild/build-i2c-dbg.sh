#!/bin/bash

cd ~/src/i2c_dbg
ls /usr/bin
make MACHINE=fs-bmc-hf
make MACHINE=rpi
make MACHINE=qemu
cp -r build/* ~/artifacts