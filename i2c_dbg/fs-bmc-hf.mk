#
# FS1600.mk
#
# Copyright (c) 2022. Fungible,inc.
# All Rights Reserved.
#


UNAME:=$(shell uname -m)

ifeq ($(UNAME),arm)
CROSS_COMPILE:=
else
CROSS_COMPILE:=arm-linux-gnueabihf-
endif

CPPFLAGS:= -DMAX_GLIBC_MINOR=31
LDLIBS:= -li2c
OBJECTS+=$(BUILD_DIR)/linux_i2c_intf.o
