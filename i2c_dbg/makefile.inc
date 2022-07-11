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
	$(STRIP) $@

$(BUILD_DIR)/%.o: %.cpp | $(BUILD_DIR)
	$(COMPILE.cc) -o $@ $<

$(BUILD_DIR):
	mkdir -p $@
clean:
	-rm -rf $(BUILD_DIR)

$(INSTALL_TARGET):
	mkdir -p $@

install: all | $(INSTALL_TARGET)
	install $(BUILD_DIR)/i2c_dbg.so $(INSTALL_TARGET)
	install bmc_sbp_chal.py $(INSTALL_TARGET)

