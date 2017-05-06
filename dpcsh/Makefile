
# OS
OS := $(shell uname)

SDKDIR ?= ../../FunSDK

# define header and library location in FunSDK
CFLAGS ?= -I $(SDKDIR)/FunSDK -L $(SDKDIR)/lib/${OS}/ -lfunclient ../../FunOS/build/posix/obj/bsd/bsd_utils.o

# XXX: compatibility with FunOS build parameters
LDFLAGS += -fsanitize=address

dpcsh: dpcsh.c web.c

install: dpcsh
	cp dpcsh $(SDKDIR)/bin

clean:
	rm dpcsh
