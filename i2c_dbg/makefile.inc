# makefile.inc
#
# shared definitions for building i2c_dbg.so
#
# Copyright (c) 2021 Fungible,Inc.
# All Rights Reserved
#
#

all: $(BUILD_DIR)/i2c_dbg.so

$(BUILD_DIR)/i2c_dbg.so: $(BUILD_DIR)/i2c_chal.o
	$(LINK.o) -o $@ $< $(LDLIBS)
	strip $@

$(BUILD_DIR)/%.o: %.cpp | $(BUILD_DIR)
	$(COMPILE.cc) -o $@ $<

$(BUILD_DIR):
	mkdir -p $@
clean:
	-rm -rf $(BUILD_DIR)
