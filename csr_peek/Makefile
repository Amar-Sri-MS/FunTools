# Basic Makefile

OS := $(shell uname)
# The build is where our SDK is rooted

SDKDIR ?= ${WORKSPACE}/FunSDK
CFG_DIR ?= $(SDKDIR)/FunSDK/chip/f1/hw/yaml/
TMPL_FILE ?= csr/template/csr_filter.yaml
INC_DIR ?= `pwd`/csr/export/include
LIB_DIR ?= `pwd`/csr/export/lib

all: csrsh

csrsh: $(LIB_DIR)/csrlib.a
	CSR_LIB=$(LIB_DIR) CSR_INC=$(INC_DIR) INSTALL_DIR=`pwd` make -C csr-shell csrsh-install
	chmod +x csrsh

$(LIB_DIR)/csrlib.a:
	PYTHONPATH=$(PYTHONPATH):$(shell pwd) bin/csr-slurp \
		-d ${CFG_DIR} \
		-f $(TMPL_FILE) \
		-c $(SDKDIR)/FunSDK/config/csr \
		-g                             \
		-i $(INC_DIR)                  \
		-l $(LIB_DIR)

.PHONY: clean
clean:
	rm -f $(LIB_DIR)/libcsr.a
	rm -f $(INC_DIR)/*
	make -C csr-shell clean
