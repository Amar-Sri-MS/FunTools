WORKSPACE ?= ../..
SDKDIR ?= $(WORKSPACE)/FunSDK
SDK_INSTALL_DIR ?= $(SDKDIR)

### Just install the scripts

all: install

install: install-logtools

clean:
	echo nothing to clean

### Python script install targets for projectdb targets

LOG_ETW_DIR = $(SDK_INSTALL_DIR)/bin/scripts/etw

install-logtools:
	mkdir -p $(SDK_INSTALL_DIR)/bin/scripts
	install fond_search $(SDK_INSTALL_DIR)/bin/scripts
	install funos_events $(SDK_INSTALL_DIR)/bin/scripts
	install funos_timestamp $(SDK_INSTALL_DIR)/bin/scripts
	install funos_log_splitter $(SDK_INSTALL_DIR)/bin/scripts
	install funos_log_merger $(SDK_INSTALL_DIR)/bin/scripts
	mkdir -p $(LOG_ETW_DIR)
	install etw/etw_to_structured_log.py $(LOG_ETW_DIR)
	install etw/default_log.tmpl $(LOG_ETW_DIR)
	install etw/default_typemap.json $(LOG_ETW_DIR)
