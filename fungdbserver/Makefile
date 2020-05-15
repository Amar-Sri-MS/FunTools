CFLAGS = -g
CXXFLAGS = -g -I${WORKSPACE}/FunSDK/include
CC=gcc
CXX=g++

WORKSPACE ?= ../..
SDKDIR ?= $(WORKSPACE)/FunSDK
SDK_INSTALL_DIR ?= $(SDKDIR)

### Default to C targets for buildling locally 

all: hbm_unshard ddr_unshard ddr_address_test

clean:
	/bin/rm -f hbm_unshard ddr_unshard ddr_unshard_test *.o

hbm_unshard: hbm_unshard.o
	$(CC) ${CFLAGS} -o hbm_unshard hbm_unshard.o

ddr_unshard: ddr_unshard.o ddr_address.h ddr_address.o
	$(CC) ${CFLAGS} -o ddr_unshard ddr_unshard.o ddr_address.o

ddr_address_test: ddr_address_test.o ddr_address.h ddr_address.o $(SDKDIR)/lib/gtest.a
	$(CXX) ${CFLAGS} -o ddr_address_test ddr_address_test.o ddr_address.o ${SDK}/lib/gtest.a -lpthread


### Python script install targtes for projectdb targets

install-fungdbserver:
	mkdir -p $(SDK_INSTALL_DIR)/bin/scripts
	install excat.py $(SDK_INSTALL_DIR)/bin/scripts
	install uuid_extract.py $(SDK_INSTALL_DIR)/bin/scripts
	install fungdbserver.py $(SDK_INSTALL_DIR)/bin/scripts
	install bulk_publish.py $(SDK_INSTALL_DIR)/bin/scripts
