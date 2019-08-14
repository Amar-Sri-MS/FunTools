hbm_dump_pcie:
	gcc -o hbm_dump_pcie hbm_dump_pcie.c

install: hbm_dump_pcie
	mkdir -p $(SDK_INSTALL_DIR)/bin/$(OS)/$(ARCH)
	cp hbm_dump_pcie $(SDK_INSTALL_DIR)/bin/$(OS)/$(ARCH)

