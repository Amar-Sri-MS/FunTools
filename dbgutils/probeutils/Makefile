CC ?= gcc
SDKDIR ?= $(WORKSPACE)/FunSDK

pcieproxy-csr1.o : pcieproxy-csr.c
	$(CC) -c -I $(SDKDIR)/FunSDK -o $@ $<

pcieproxy-csr2.o : pcieproxy-csr.c
	$(CC) -c -I $(SDKDIR)/FunSDK -DCONFIG_CSR_VERSION_2 -o $@ $<

pcieproxy: pcieproxy.c pcieproxy-csr1.o pcieproxy-csr2.o
	$(CC) -I $(SDKDIR)/FunSDK -o $@ $^

hbm_dump_pcie: hbm_dump_pcie.c
	$(CC) -o hbm_dump_pcie hbm_dump_pcie.c

install: hbm_dump_pcie
	mkdir -p $(SDK_INSTALL_DIR)/bin/$(OS)/$(ARCH)
	cp hbm_dump_pcie $(SDK_INSTALL_DIR)/bin/$(OS)/$(ARCH)

