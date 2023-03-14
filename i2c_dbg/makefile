# makefile
#
# build i2c_dbg.so
#
# Copyright (c) 2021-2022 Fungible,Inc.
# All Rights Reserved
#
#

MACHINE?=FS1600


BUILD_DIR:=build/$(MACHINE)
INSTALL_TARGET:=$(SDK_INSTALL_DIR)/bin/i2c_dbg/$(MACHINE)


include $(MACHINE).mk

CXX:=$(CROSS_COMPILE)g++
CC:=$(CROSS_COMPILE)g++
STRIP:=$(CROSS_COMPILE)strip

CXXFLAGS+= -Os
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

install: all | $(INSTALL_TARGET)
	install $(BUILD_DIR)/i2c_dbg.so $(INSTALL_TARGET)
	install bmc_sbp_chal.py $(INSTALL_TARGET)
