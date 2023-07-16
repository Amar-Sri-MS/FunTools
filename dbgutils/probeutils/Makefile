CC ?= gcc
SDKDIR ?= $(WORKSPACE)/FunSDK
PCIEPROXY_DIR := $(SDK_INSTALL_DIR)/pcieproxy/$(ARCH)

# these flags are required for the library, there's no harm
# in also using them for the app build, so it's more simple
# to always use them, as otherwise we'd need separate object
# files for each target
PCIEPROXY_LIB_FLAGS = -fvisibility=hidden -fPIC

PCIEPROXY_FLAGS = -I $(SDKDIR)/FunSDK -I $(SDKDIR) $(PCIEPROXY_LIB_FLAGS) -I $(SDKDIR)/FunSDK/funosrt/include

BUILD_DIR := build/$(ARCH)

$(BUILD_DIR):
	mkdir -p $@

$(BUILD_DIR)/pcieproxy-csr1.o : pcieproxy-csr.c | $(BUILD_DIR)
	$(CC) -c $(PCIEPROXY_FLAGS) -o $@ $<

$(BUILD_DIR)/pcieproxy-csr2.o : pcieproxy-csr.c | $(BUILD_DIR)
	$(CC) -c $(PCIEPROXY_FLAGS) -DCONFIG_CSR_VERSION_2 -o $@ $<

pcieproxy-csr-o := $(BUILD_DIR)/pcieproxy-csr2.o $(BUILD_DIR)/pcieproxy-csr1.o

$(BUILD_DIR)/pcieproxy: pcieproxy.c $(pcieproxy-csr-o) | $(BUILD_DIR)
	$(CC) $(PCIEPROXY_FLAGS) -DBUILD_SERVER -o $@ $^

$(BUILD_DIR)/libpcieproxy.so: pcieproxy.c $(pcieproxy-csr-o) | $(BUILD_DIR)
	$(CC) $(PCIEPROXY_FLAGS) -shared -DBUILD_LIBRARY -o $@ $^

$(PCIEPROXY_DIR)/lib $(PCIEPROXY_DIR)/include :
	mkdir -p $@

install-lib: $(BUILD_DIR)/libpcieproxy.so libpcieproxy.h | $(PCIEPROXY_DIR)/lib $(PCIEPROXY_DIR)/include
	install $(BUILD_DIR)/libpcieproxy.so $(PCIEPROXY_DIR)/lib
	install libpcieproxy.h $(PCIEPROXY_DIR)/include

$(BUILD_DIR)/hbm_dump_pcie: hbm_dump_pcie.c | $(BUILD_DIR)
	$(CC) -o $@ hbm_dump_pcie.c

install: $(BUILD_DIR)/hbm_dump_pcie $(BUILD_DIR)/pcieproxy
	mkdir -p $(SDK_INSTALL_DIR)/bin/$(OS)/$(ARCH)
	cp $? $(SDK_INSTALL_DIR)/bin/$(OS)/$(ARCH)

.PHONY: install install-lib
