WORKSPACE ?= ../..
SDKDIR ?= $(WORKSPACE)/FunSDK
SDK_INSTALL_DIR ?= $(SDKDIR)

### Python script install targets for projectdb targets

install-ins-cyc:
	mkdir -p $(SDK_INSTALL_DIR)/bin/scripts
	install instr_dasm.py $(SDK_INSTALL_DIR)/bin/scripts
	install instr_count.py $(SDK_INSTALL_DIR)/bin/scripts
	install instr_count_diff.py $(SDK_INSTALL_DIR)/bin/scripts
	install instr_count_query.py $(SDK_INSTALL_DIR)/bin/scripts

clean:
	echo "nothing to clean"
