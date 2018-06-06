# Basic Makefile

OS := $(shell uname)
# The build is where our SDK is rooted

SDKDIR ?= `pwd`/../../FunSDK
CFG_DIR ?= $(SDKDIR)/FunSDK/chip/f1/hw/yaml/
TMPL_FILE ?= csr/template/csr_filter.yaml
INC_DIR ?= `pwd`/csr/export/include
LIB_DIR ?= `pwd`/csr/export/lib
CSR_JSON ?= csr_metadata.json

# This stuff is needed for FunSDK scripts
# to pull artifacts from here

SDK_INSTALL_DIR ?= $(SDKDIR)

# This should be the first target
ifeq ($(OS), Darwin)
build: build_mac
else
ifeq ($(OS), Linux)
build: build_linux
endif
endif

build_mac: $(LIB_DIR)/csrlib.a
	CSR_LIB=$(LIB_DIR) CSR_INC=$(INC_DIR) INSTALL_DIR=`pwd` SDKDIR=$(SDKDIR) make -C csr-shell csrsh-install
	chmod +x csrsh

build_linux:
	PYTHONPATH=$(PYTHONPATH):$(shell pwd) bin/csr-slurp \
		-d ${CFG_DIR} \
		-f $(TMPL_FILE) \
		-c .

$(LIB_DIR)/csrlib.a:
	PYTHONPATH=$(PYTHONPATH):$(shell pwd) bin/csr-slurp \
		-d ${CFG_DIR}                               \
		-f $(TMPL_FILE)                             \
		-c .                                        \
		-g                                          \
		-i $(INC_DIR)                               \
		-l $(LIB_DIR)

install: build
	mkdir -p $(SDK_INSTALL_DIR)/FunSDK/config/csr
	rsync -av $(CSR_JSON) $(SDK_INSTALL_DIR)/FunSDK/config/csr

.PHONY: clean
clean:
	rm -f $(LIB_DIR)/libcsr.a
	rm -f $(INC_DIR)/*
	make -C csr-shell clean
	rm -f csrsh
	rm -f *.json
