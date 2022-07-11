# makefile
#
# build ARM i2c_dbg.so
#
# Copyright (c) 2021 Fungible,Inc.
# All Rights Reserved
#
#


BUILD_DIR:=arm
CROSS_COMPILE:=arm-linux-gnueabi-

CXX:=$(CROSS_COMPILE)g++
CC:=$(CROSS_COMPILE)g++
STRIP:=$(CROSS_COMPILE)strip
CXXFLAGS:= -Os
LDFLAGS = -L. -static-libgcc -static-libstdc++ -Wl,-rpath=/usr/local/lib --shared
LDLIBS = -li2c

INSTALL_TARGET:=$(SDK_INSTALL_DIR)/bin/i2c_dbg

include makefile.inc

