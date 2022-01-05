##
##  Makefile
##
##  Created by Charles Gray on 2020-10-21.
##  Copyright (c) 2020 Fungible. All rights reserved.
##

# OS
OS := $(shell uname)

# arch
ARCH := $(shell uname -m)

SDKDIR ?= ../../FunSDK
SDK_INSTALL_DIR ?= $(SDKDIR)

all: pcicfgutil

# define header and library location in FunSDK
CFLAGS ?= -I $(SDKDIR)/FunSDK/funosrt/include  \
	  -I $(SDKDIR) -Wall -Werror

# XXX: compatibility with FunOS build parameters
LDFLAGS_ASAN ?= -fsanitize=address
ifeq ($(OS),Linux)
#asan library linking does not work for Linux
LDFLAGS += -L $(SDKDIR)/lib/$(OS)/noasan/$(ARCH) -lfunclient -lm -ldl
DARWIN_ASAN_FIXUP :=
else
LDFLAGS += -L $(SDKDIR)/lib/$(OS)/$(ARCH) -lfunclient -lm $(LDFLAGS_ASAN)
endif

SRC += pcicfgutil.c

pcicfgutil: pcicfgutil.c
	$(CC) -o pcicfgutil $(SRC) $(CFLAGS) $(LDFLAGS)


ifeq ($(OS),Darwin)
# FF: since the path and the compatibility of the ASAN library keeps changing,
# find the copy used to build the jsonutil and copy it into the same directory
# as the jsonutil exectuable so it can always find it.
# $ otool -L jsonutil
#jsonutil:
#	/usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1252.200.5)
#	@rpath/libclang_rt.asan_osx_dynamic.dylib (compatibility version 0.0.0, current version 0.0.0)
#Load command 14
#          cmd LC_RPATH
#      cmdsize 32
#         path @executable_path (offset 12)
DARWIN_ASAN_FIXUP := find /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/ -name libclang_rt.asan_osx_dynamic.dylib -exec cp {} $(SDK_INSTALL_DIR)/bin/$(OS)/$(ARCH) \;
endif


install: pcicfgutil
	mkdir -p $(SDK_INSTALL_DIR)/bin/$(OS)/$(ARCH)
	cp pcicfgutil $(SDK_INSTALL_DIR)/bin/$(OS)/$(ARCH)
	$(DARWIN_ASAN_FIXUP)

clean:
	-rm -f pcicfgutil
