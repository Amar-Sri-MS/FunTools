CXX=g++
CXXFLAGS=-Wall -O3 -g -std=c++11 -I$(CSR_INC)

driver_src = $(wildcard test/*.cpp)

lib_src = $(wildcard *.cpp)

lib_obj = $(lib_src:.cpp=.o)

dummy_lib=libdummy.a

AR = ar
#ARFLAGS = crf
ARFLAGS = cr
#STRIP = strip --strip-unneeded
RANLIB = ranlib

.PHONY: clean

$(dummy_lib): $(lib_obj)
	#$(STRIP) $^
	$(AR) $(ARFLAGS) $@ $^
	$(RANLIB) $@

clean:
	rm -f *.o
	rm -f $(dummy_lib)
