# Basic Makefile
# First, install this module
# Then do a make cfg_upd to pull in the CSR configs from NFS Mount
# Then, do a make csr to create the csr-library
#
# Do a make clean to remove the derived files (except the pulled in CSR)
# Do a make distclean to remove all the CSR configurations as well

SUDO = sudo
INDIR = jsb

all: build

.PHONY: build clean libcsr cfg_pull cfg
build:
	$(SUDO) python setup.py install --record files.txt

libcsr:
	$(SUDO) apt-get install astyle
	cd csr-rt && astyle -c gen/csr_gen.cpp &&  make

cfg:build
	csr-slurp -i csr/csr_cfg -o csr-rt/gen


cfg_pull:build
	sudo apt-get install nfs-common
	cd csr; csr-get -i $(INDIR)

clean:
	cat files.txt | sudo xargs rm -rf
	$(SUDO) rm -rf dist
	$(SUDO) rm -rf build
	$(SUDO) rm -rf *.egg-info
	$(SUDO) rm -f files.txt
	cd csr-rt; make clean

distclean: clean
	cd csr/csr_cfg && rm -rf *
	cd csr-rt; make distclean
