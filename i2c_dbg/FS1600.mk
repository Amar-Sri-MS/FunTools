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
CROSS_COMPILE:=arm-linux-gnueabi-
endif

CPPFLAGS:= -DFS1600=1 -DMAX_GLIBC_MINOR=31
LDLIBS:= -li2c
