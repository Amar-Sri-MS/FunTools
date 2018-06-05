# Basic Makefile

OS := $(shell uname)
# The build is where our SDK is rooted

SDKDIR ?= ${WORKSPACE}/FunSDK
CFG_DIR ?= $(SDKDIR)/FunSDK/chip/f1/hw/yaml/
TMPL_FILE ?= csr/template/csr_filter.yaml
INC_DIR ?= `pwd`/csr/export/include
LIB_DIR ?= `pwd`/csr/export/lib


all: csrsh

# Install Pipenv for user if necessary
ifeq ($(PYTHONUSERBASE),)
	PYTHONUSERBASE := $(HOME)/.local
endif

PIPENV := $(or $(wildcard $(PYTHONUSERBASE)/bin/pipenv),\
	$(wildcard /usr/local/bin/pipenv),\
	$(wildcard /usr/bin/pipenv),\
	$(PYTHONUSERBASE/bin/pipenv))
$(PYTHONUSERBASE)/bin/pipenv:
	pip install --user pipenv

# Create venv if not exists
VENV = $(or $(shell $(PIPENV) --venv 2>/dev/null),venv)

.PHONY: venv
venv: | $(PIPENV)
	$(PIPENV) install --verbose -e . --dev

ifneq ($(VENV), venv)
	touch $(VENV)
$(VENV): Pipfile Pipfile.lock
	$(MAKE) venv
endif

.PHONY: clean

csrsh: $(LIB_DIR)/csrlib.a
	CSR_LIB=$(LIB_DIR) CSR_INC=$(INC_DIR) make -C csr-shell csrsh
$(LIB_DIR)/csrlib.a: $(VENV)
	pipenv run csr-slurp \
		-d ${CFG_DIR} \
		-f $(TMPL_FILE) \
		-c $(SDKDIR)/FunSDK/config/csr \
		-g                             \
		-i $(INC_DIR)                  \
		-l $(LIB_DIR)

clean: | clean_venv
	make -C csr-shell distclean
	rm -f *.o
clean_venv:
	@if [ -f $(PIPENV) ] && $(PIPENV) --venv > /dev/null 2>&1; then $(PIPENV) --rm; fi
	@rm -rf csr_slurp.egg-info
