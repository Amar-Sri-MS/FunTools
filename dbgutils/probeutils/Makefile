CC ?= gcc
SDKDIR ?= $(WORKSPACE)/FunSDK

PCIEPROXY_FLAGS = -I $(SDKDIR)/FunSDK -I $(SDKDIR)

pcieproxy-csr1.o : pcieproxy-csr.c
	$(CC) -c $(PCIEPROXY_FLAGS) -o $@ $<

pcieproxy-csr2.o : pcieproxy-csr.c
	$(CC) -c $(PCIEPROXY_FLAGS) -DCONFIG_CSR_VERSION_2 -o $@ $<

pcieproxy: pcieproxy.c pcieproxy-csr1.o pcieproxy-csr2.o
	$(CC) $(PCIEPROXY_FLAGS) -o $@ $^

hbm_dump_pcie: hbm_dump_pcie.c
	$(CC) -o hbm_dump_pcie hbm_dump_pcie.c

install: hbm_dump_pcie
	mkdir -p $(SDK_INSTALL_DIR)/bin/$(OS)/$(ARCH)
	cp hbm_dump_pcie $(SDK_INSTALL_DIR)/bin/$(OS)/$(ARCH)

