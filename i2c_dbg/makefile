# makefile
#
# build ARM i2c_dbg.so
#
# Copyright (c) 2021 Fungible,Inc.
# All Rights Reserved
#
#


BUILD_DIR:=arm

CXX:=arm-linux-gnueabi-g++
CC:=arm-linux-gnueabi-g++
CXXFLAGS:= -Os
LDFLAGS = -L. -static-libgcc -static-libstdc++ -Wl,-rpath=/usr/local/lib --shared
LDLIBS = -li2c

include makefile.inc
