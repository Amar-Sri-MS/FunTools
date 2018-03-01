# Need this to cleanly uninstall funnel-as

SUDO = sudo

all: build

.PHONY: build clean csr cfg_upd
build:
	$(SUDO) python setup.py install --record files.txt
csr: 
	cd csr-rt; make

cfg_upd:build
	cd csr; csr-get

clean:
	cat files.txt | sudo xargs rm -rf
	$(SUDO) rm -rf dist
	$(SUDO) rm -rf build
	$(SUDO) rm -rf *.egg-info
	$(SUDO) rm -f files.txt

distclean: clean
	cd csr/csr_cfg && rm -rf *
