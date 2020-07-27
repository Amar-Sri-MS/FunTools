SDKDIR ?= ../../FunSDK
SDK_INSTALL_DIR ?= $(SDKDIR)

# Directory where we install the working version.
NVDIMM_FW_INSTALL_DIR = $(SDK_INSTALL_DIR)/FunSDK/nvdimm_fw

BUILD_VERSION = 1
DL_SERVER ?= http://dochub.fungible.local/doc/jenkins/third_party/nvdimm/$(BUILD_VERSION)/
DL_FILES := \
	Amber4X-U-PGEM_Firmware-V1.40.zip River16-DDR4_NVDIMM_Firmware-V2.5.zip
DL_DIR := dl

IMAGE_FILES := \
	AGIGA-SRI-PGM5XX.AMBER4X-V1.40-UPGRADE_signed.img \
	AGIGA-SRI-RAM4PA.RIVER16-V2.50-UPGRADE_ALL-signed.img

$(DL_DIR):
	@mkdir -p $@

$(foreach f, $(DL_FILES), $(DL_DIR)/$f): | $(DL_DIR)
	cd $(DL_DIR) && wget $(DL_SERVER)/$(@F)

download: $(foreach f, $(DL_FILES), $(DL_DIR)/$f)


all: download
	cd $(DL_DIR) && find -name '*.zip' -exec unzip -jo {} \;

# install to SDK
install:
	mkdir -p $(NVDIMM_FW_INSTALL_DIR)
	rsync -ar $(foreach f, $(IMAGE_FILES), $(DL_DIR)/$(f)) $(NVDIMM_FW_INSTALL_DIR)
	rsync -ar *.version *.json $(NVDIMM_FW_INSTALL_DIR)

clean:
	@rm -rf $(DL_DIR)
