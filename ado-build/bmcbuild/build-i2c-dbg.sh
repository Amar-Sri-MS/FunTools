#!/bin/bash

cd ~/src/i2c_dbg
make
make MACHINE=fs-bmc-hf
make MACHINE=rpi
make MACHINE=qemu
cp -r build/* ~/artifacts