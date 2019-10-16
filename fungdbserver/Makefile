CFLAGS = -g
CXXFLAGS = -g -I${WORKSPACE}/FunSDK/include
CC=gcc
CXX=g++

SDK=${WORKSPACE}/FunSDK

all: hbm_unshard ddr_unshard ddr_address_test

clean:
	/bin/rm -f hbm_unshard ddr_unshard ddr_unshard_test *.o

hbm_unshard: hbm_unshard.o
	$(CC) ${CFLAGS} -o hbm_unshard hbm_unshard.o

ddr_unshard: ddr_unshard.o ddr_address.h ddr_address.o
	$(CC) ${CFLAGS} -o ddr_unshard ddr_unshard.o ddr_address.o

ddr_address_test: ddr_address_test.o ddr_address.h ddr_address.o ${SDK}/lib/gtest.a
	$(CXX) ${CFLAGS} -o ddr_address_test ddr_address_test.o ddr_address.o ${SDK}/lib/gtest.a -lpthread
