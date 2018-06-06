ifeq ($(OS),Darwin)
  CXX=clang++
else
ifeq ($(OS),Linux)
  CXX=g++
endif
endif


SDKDIR ?= `pwd`/../../../FunSDK
BACKEND=backends/dummy
BACKEND_LIB=dummy
BACKEND_LIBRARY=$(BACKEND)/libdummy.a
BACKEND_INC=-I backends/dummy


#CXXFLAGS=-Wall -O3 -g -std=c++11 $(LIBINC)
CXXFLAGS=-Wall -std=c++11 -I$(CSR_INC)

#driver_src = $(wildcard test/*.cpp)
driver_src=test/prog.cpp
driver_obj=test/prog.o

LIBS= -L$(CSR_LIB) -L $(BACKEND) -lcsr -l$(BACKEND_LIB)


.PHONY: clean

test_driver: $(driver_obj) $(BACKEND_LIBRARY)
	$(CXX) $(CXXFLAGS) -o $@ $(driver_obj) $(LIBS)
csrsh: 
	CSR_INC=$(CSR_INC) CSR_LIB=$(CSR_LIB) SDKDIR=$(SDKDIR) make -C frontends/csrsh csrsh
csrsh-install:
	CSR_INC=$(CSR_INC) CSR_LIB=$(CSR_LIB) INSTALL_DIR=$(INSTALL_DIR) SDKDIR=$(SDKDIR) make -C frontends/csrsh csrsh-install

$(BACKEND_LIBRARY):
	CSR_INC=$(CSR_INC) make -C $(BACKEND)
clean:
	rm -f test/*.o
	rm -f test_driver
	make -C $(BACKEND) clean
	make -C frontends/csrsh clean
