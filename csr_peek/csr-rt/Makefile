CXX=g++

BACKEND=backends/dummy
BACKEND_LIB=dummy
BACKEND_LIBRARY=$(BACKEND)/libdummy.a
BACKEND_INC=-I backends/dummy

LIBINC=-I include -I gen

#CXXFLAGS=-Wall -O3 -g -std=c++11 $(LIBINC)
CXXFLAGS=-Wall -std=c++11 $(LIBINC)

#driver_src = $(wildcard test/*.cpp)
driver_src=test/prog.cpp
driver_obj=test/prog.o

lib_src = $(wildcard src/*.cpp) \
		  $(wildcard gen/*.cpp)

lib_obj = $(lib_src:.cpp=.o)
#driver_obj = $(driver_src:.cpp=.o)

csr_lib=libcsr.a


LIBS= -L. -L $(BACKEND) -lcsr -l$(BACKEND_LIB)

AR = ar
ARFLAGS = crf
STRIP = strip --strip-unneeded
RANLIB = ranlib

.PHONY: clean

test_driver: $(csr_lib) $(driver_obj) $(BACKEND_LIBRARY)
	$(CXX) $(CXXFLAGS) -o $@ $(driver_obj) $(LIBS)

$(driver_obj): $(driver_src)
	$(CXX) $(CXXFLAGS) $(BACKEND_INC) -c $^ -o $@

$(csr_lib): $(lib_obj)
	$(STRIP) $^
	$(AR) $(ARFLAGS) $@ $^
	$(RANLIB) $@
$(BACKEND_LIBRARY):
	cd $(BACKEND) && make
clean:
	rm -f test/*.o
	rm -f gen/*.o
	rm -f src/*.o
	rm -f libcsr.a
	rm -f test_driver
	cd $(BACKEND) && make clean
distclean:
	rm -f gen/*
