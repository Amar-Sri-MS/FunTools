
# OS
OS := $(shell uname)

# arch
ARCH := $(shell uname -m)

SDKDIR ?= ../../FunSDK
SDK_INSTALL_DIR ?= $(SDKDIR)

all: snap_diff

# define header and library location in FunSDK
CFLAGS ?= -I $(SDKDIR)/FunSDK  \
	-I $(SDKDIR)

# XXX: compatibility with FunOS build parameters
LDFLAGS_ASAN ?= -fsanitize=address
ifeq ($(OS),Linux)
#asan library linking does not work for Linux
LDFLAGS += -L $(SDKDIR)/lib/$(OS)/noasan/$(ARCH) -lfunclient -lm -ldl
DARWIN_ASAN_FIXUP :=
else
LDFLAGS += -L $(SDKDIR)/lib/$(OS)/$(ARCH) -coverage -lfunclient -lm $(LDFLAGS_ASAN)
endif

SRC += snap_diff.c

snap_diff: snap_diff.c
	$(CC) -o snap_diff $(SRC) $(CFLAGS) $(LDFLAGS)

ifeq ($(OS),Darwin)
DARWIN_ASAN_FIXUP := find /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/ -name libclang_rt.asan_osx_dynamic.dylib -exec cp {} $(SDK_INSTALL_DIR)/bin/$(OS)/$(ARCH) \;
endif


install: snap_diff
	mkdir -p $(SDK_INSTALL_DIR)/bin/$(OS)/$(ARCH)
	cp snap_diff $(SDK_INSTALL_DIR)/bin/$(OS)/$(ARCH)
	$(DARWIN_ASAN_FIXUP)

clean:
	-rm -f snap_diff
