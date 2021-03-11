# OS
OS := $(shell uname)

SDKDIR ?= ../../FunSDK
ARCH = ${shell uname -m}

# define header and library location in FunSDK
CFLAGS ?= -I$(SDKDIR) -I$(SDKDIR)/FunSDK/ -L $(SDKDIR)/lib/${OS}/ -L $(SDKDIR)/lib/${OS}/${ARCH} -lfunclient -lcurses

# XXX: compatibility with FunOS build parameters
LDFLAGS += -fsanitize=address

funtop: funtop.c

install: funtop
	cp funtop $(SDKDIR)/bin

clean:
	rm funtop
