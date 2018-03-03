CXX=g++
CXXFLAGS=-Wall -O3 -g -std=c++11 -I include -I gen

driver_src = $(wildcard test/*.cpp)

lib_src = $(wildcard src/*.cpp) \
		  $(wildcard gen/*.cpp)

lib_obj = $(lib_src:.cpp=.o)
driver_obj = $(driver_src:.cpp=.o)

csr_lib=libcsr.a
LIBS= -L. -lcsr

AR = ar
ARFLAGS = crf
STRIP = strip --strip-unneeded
RANLIB = ranlib

.PHONY: clean

test_driver: $(csr_lib) $(driver_obj)
	$(CXX) $(CXXFLAGS) -o $@ $(driver_obj) $(LIBS)

$(csr_lib): $(lib_obj)
	$(STRIP) $^
	$(AR) $(ARFLAGS) $@ $^
	$(RANLIB) $@

clean:
	rm -f test/*.o
	rm -f gen/*.o
	rm -f src/*.o
	rm -f libcsr.a
	rm -f test_driver
distclean:
	rm -f gen/*
