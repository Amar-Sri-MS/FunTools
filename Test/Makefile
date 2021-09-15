## Simple makefile to install scripts into FunSDK

WORKSPACE ?= ../..
SDKDIR ?= $(WORKSPACE)/FunSDK
SDK_INSTALL_DIR ?= $(SDKDIR)

### Just install the scripts

all: install

install: install-scripts

clean:
	echo nothing to clean

### Python script install targets for projectdb targets

install-scripts:
	mkdir -p $(SDK_INSTALL_DIR)/bin/scripts
	install tools/cluster/si_api.py $(SDK_INSTALL_DIR)/bin/scripts

