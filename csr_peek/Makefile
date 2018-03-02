# Basic Makefile
# First, install this module
# Then do a make cfg_upd to pull in the CSR configs from NFS Mount
# Then, do a make csr to create the csr-library
#
# Do a make clean to remove the derived files (except the pulled in CSR)
# Do a make distclean to remove all the CSR configurations as well

SUDO = sudo

all: build

.PHONY: build clean libcsr cfg_pull cfg
build:
	$(SUDO) python setup.py install --record files.txt

libcsr: 
	cd csr-rt; make

cfg:build
	csr-slurp -i csr/csr_cfg -o csr-rt/gen


cfg_pull:build
	cd csr; csr-get

clean:
	cat files.txt | sudo xargs rm -rf
	$(SUDO) rm -rf dist
	$(SUDO) rm -rf build
	$(SUDO) rm -rf *.egg-info
	$(SUDO) rm -f files.txt
	cd csr-rt; make clean

distclean: clean
	cd csr/csr_cfg && rm -rf *
	#cd csr-rt; make distclean
