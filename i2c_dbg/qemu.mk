#
# QEMU.mk
#
# Copyright (c) 2023, Microsoft.
# All Rights Reserved.
#

UNAME:=$(shell uname -m)

CROSS_COMPILE:=

CPPFLAGS:= -DUSE_POSIX_SOCKET -fPIC
LDLIBS:=
OBJECTS+=$(BUILD_DIR)/posix_socket_intf.o
