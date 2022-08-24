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
	install s3util.py $(SDK_INSTALL_DIR)/bin/scripts
	install httpfile.py $(SDK_INSTALL_DIR)/bin/scripts
	install gz2idgz.py $(SDK_INSTALL_DIR)/bin/scripts
	install rdsstat.py $(SDK_INSTALL_DIR)/bin/scripts
	install update-dpu.py $(SDK_INSTALL_DIR)/bin/scripts
	install dpuctl.py $(SDK_INSTALL_DIR)/bin/scripts
	install exprom-hdrgen.py $(SDK_INSTALL_DIR)/bin/scripts
	install issu $(SDK_INSTALL_DIR)/bin/scripts
	install deploy-funtools.scripts.sh $(SDK_INSTALL_DIR)/bin/scripts
	install decode_action $(SDK_INSTALL_DIR)/bin/scripts

