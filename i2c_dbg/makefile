# makefile
#
# build i2c_dbg.so
#
# Copyright (c) 2021-2022 Fungible,Inc.
# All Rights Reserved
#
#

MACHINE?=fs-bmc

git_version := $(shell git describe)

BUILD_DIR:=build/$(MACHINE)
INSTALL_TARGET:=$(SDK_INSTALL_DIR)/bin/i2c_dbg/$(MACHINE)
SO_SRCS_TAR:=i2c_dbg_so_src.tgz

include $(MACHINE).mk

CXX:=$(CROSS_COMPILE)g++
CC:=$(CROSS_COMPILE)g++
STRIP:=$(CROSS_COMPILE)strip


CXXFLAGS+= -Os -DGIT_VERSION=$(git_version)
LDFLAGS+= -L. -static-libgcc -static-libstdc++ -Wl,-rpath=/usr/local/lib --shared


all: $(BUILD_DIR)/i2c_dbg.so

OBJECTS+= $(BUILD_DIR)/i2c_chal.o
OBJECTS+= $(BUILD_DIR)/shared_defs.o


$(BUILD_DIR)/i2c_dbg.so: $(OBJECTS)
	$(LINK.o) -o $@ $^ $(LDLIBS)
	$(STRIP) $@

$(BUILD_DIR)/%.o: %.cpp | $(BUILD_DIR)
	$(COMPILE.cc) -o $@ $<

$(BUILD_DIR):
	mkdir -p $@

clean:
	-rm -rf build

$(INSTALL_TARGET):
	mkdir -p $@

$(SO_SRCS_TAR):
	tar -czf $(SO_SRCS_TAR) --exclude bmc_sbp_chal.py \
	`git ls-tree -r HEAD --name-only`


install: $(SO_SRCS_TAR) all | $(INSTALL_TARGET)
	install $(BUILD_DIR)/i2c_dbg.so $(INSTALL_TARGET)
	install bmc_sbp_chal.py $(INSTALL_TARGET)
	install $(SO_SRCS_TAR)  $(INSTALL_TARGET)/..
