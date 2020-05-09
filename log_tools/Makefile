WORKSPACE ?= ../..
SDKDIR ?= $(WORKSPACE)/FunSDK
SDK_INSTALL_DIR ?= $(SDKDIR)

### Default to C targets for buildling locally 

all: install

install: install-logtools

### Python script install targets for projectdb targets

install-logtools:
	mkdir -p $(SDK_INSTALL_DIR)/bin/scripts
	install fond_search $(SDK_INSTALL_DIR)/bin/scripts
	install funos_events $(SDK_INSTALL_DIR)/bin/scripts
	install funos_timestamp $(SDK_INSTALL_DIR)/bin/scripts
