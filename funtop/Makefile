# OS
OS := $(shell uname)

SDKDIR ?= ../../FunSDK

# define header and library location in FunSDK
CFLAGS ?= -I$(SDKDIR) -I$(SDKDIR)/FunSDK/ -L $(SDKDIR)/lib/${OS}/ -lfunclient -lcurses

# XXX: compatibility with FunOS build parameters
LDFLAGS += -fsanitize=address

funtop: funtop.c

install: funtop
	cp funtop $(SDKDIR)/bin

clean:
	rm funtop
