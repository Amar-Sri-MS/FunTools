###
##   The build is where our SDK is rooted
#
SDKDIR ?= ../../FunSDK

###
##   Where install files go
#
SDK_INSTALL_DIR ?= $(SDKDIR)

# Directory where we install the working version of the ConfigGen
FUNSDK_INSTALL_DIR = $(SDK_INSTALL_DIR)/bin/ConfigGen


CFGGEN_SRC :=	cfg_gen.py         \
		csr_db_gen.py      \
		hu_cfg_gen.py      \
		storage_cfg_gen.py \
		jsonutils.py       \
		sku_cfg_gen.py     \
		sku_board_layer_cfg_gen.py \
		default_cfg_gen.py \
		hwcap_cfg_gen.py   \
		nu_cfg_gen.py      \
		platform_sku_c.j2  \
		platform_sku_h.j2  \
		hwcap_config_c.j2  \
		hwcap_config_h.j2  \
		mod_interface.py   \
		mod_interface_h.j2


.PHONY: test
test:
	@echo "Nothing to do"

# install to SDK
install:
	mkdir -p $(FUNSDK_INSTALL_DIR)
	rsync -R $(CFGGEN_SRC) $(FUNSDK_INSTALL_DIR)

clean:

