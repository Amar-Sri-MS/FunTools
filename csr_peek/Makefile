# Need this to cleanly uninstall funnel-as

SUDO = sudo

all: build

.PHONY: build clean csr cfg
build:
	$(SUDO) python setup.py install --record files.txt
csr: 
	cd csr-rt; make
cfg:



clean:
	cat files.txt | sudo xargs rm -rf
	$(SUDO) rm -rf dist
	$(SUDO) rm -rf build
	$(SUDO) rm -rf *.egg-info
	$(SUDO) rm -f files.txt

