# GOOGLETEST_DIR is pointer to top of tree containing build GTest.
# GOOGLETEST_DIR=/home/bowdidge/Code/googletest

CFLAGS = -g -I ${GOOGLETEST_DIR}/googletest/include
CXXFLAGS = -g -I ${WORKSPACE}/FunSDK/include -I ${GOOGLETEST_DIR}/googletest/include
LDFLAGS = -L${GOOGLETEST_DIR}/build/lib
CC=gcc
CXX=g++

WORKSPACE ?= ../..
SDKDIR ?= $(WORKSPACE)/FunSDK
SDK_INSTALL_DIR ?= $(SDKDIR)
### Default to C targets for buildling locally 

# TODO(bowdidge): Add tests to all when GOOGLETEST_DIR always present.
all: hbm_unshard ddr_unshard ddr_unshard_s2

clean:
	/bin/rm -f hbm_unshard ddr_unshard ddr_unshard_test \
	    ddr_unshard_s2 ddr_address_s2_test *.o

hbm_unshard: hbm_unshard.o
	$(CC) ${CFLAGS} -o hbm_unshard hbm_unshard.o

ddr_unshard: ddr_unshard.o ddr_address.h ddr_address.o
	$(CC) ${CFLAGS} -o ddr_unshard ddr_unshard.o ddr_address.o

ddr_unshard_s2: ddr_unshard.o ddr_address.h ddr_address_s2.o
	$(CC) ${CFLAGS} -o ddr_unshard_s2 ddr_unshard.o ddr_address_s2.o

ddr_address_test: ddr_address_test.o ddr_address.h ddr_address.o
	$(CXX) ${LDFLAGS} -o ddr_address_test ddr_address_test.o ddr_address.o -lgtest -lpthread

ddr_address_s2_test: ddr_address_s2_test.o ddr_address.h ddr_address_s2.o
	$(CXX) ${LDFLAGS} -o ddr_address_s2_test ddr_address_s2_test.o ddr_address_s2.o -lgtest -lpthread

test: ddr_address_test ddr_address_s2_test
	./ddr_address_test
	./ddr_address_s2_test

### Python script install targets for projectdb targets

install-fungdbserver: hbm_unshard ddr_unshard ddr_unshard_s2
	mkdir -p $(SDK_INSTALL_DIR)/bin/scripts
	install excat.py $(SDK_INSTALL_DIR)/bin/scripts
	install uuid_extract.py $(SDK_INSTALL_DIR)/bin/scripts
	install fungdbserver.py $(SDK_INSTALL_DIR)/bin/scripts
	install bulk_publish.py $(SDK_INSTALL_DIR)/bin/scripts

	mkdir -p ${SDK_INSTALL_DIR}/bin/Linux
	install hbm_unshard ${SDK_INSTALL_DIR}/bin/Linux/
	install ddr_unshard ${SDK_INSTALL_DIR}/bin/Linux
	install ddr_unshard_s2 ${SDK_INSTALL_DIR}/bin/Linux
