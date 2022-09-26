#
# RASPBERRY.mk
#
# Copyright (c) 2022. Fungible,inc.
# All Rights Reserved.
#

UNAME:=$(shell uname -m)

ifeq ($(UNAME),aarch64)
CROSS_COMPILE:=
else
CROSS_COMPILE:=aarch64-linux-gnu-
endif

CPPFLAGS:= -DRASPBERRY=1 -DMAX_GLIBC_MINOR=31 -fPIC
LDLIBS:=
OBJECTS+=$(BUILD_DIR)/linux_i2c_intf.o
