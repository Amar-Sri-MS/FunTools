
# Platform
OS := $(shell uname)

MACHINE ?= posix

ifeq ($(OS),Darwin)
	TOOL_ROOT := /Users/Shared/cross-el/bin
	TOOL_PREFIX := mips64el-
else
ifeq ($(OS),Linux)
	TOOL_ROOT ?= /opt/cross/bin
	TOOL_PREFIX ?= mipsel-unknown-linux-gnu-
endif
endif

ifeq ($(MACHINE),posix)
	FULLPREFIX =
	LIBDST = posix/$(OS)
else
ifeq ($(MACHINE),mips)
	FULLPREFIX = $(TOOL_ROOT)/$(TOOL_PREFIX)
	LIBDST = mips64
endif
endif

CC = $(FULLPREFIX)gcc
AR = $(FULLPREFIX)ar

BUILD = build

SDKDIR ?= ../../../FunSDK

LIBS = $(SDKDIR)/lib/$(OS)/noasan/libfunclient.a

LIB_HCI = libfunhci-$(MACHINE).a

HCI_SRC = fun_hci.c
HCI_HDR = fun_hci.h

HCI_OBJS = $(patsubst %.c,$(BUILD)/obj/%.o,$(filter %c,$(HCI_SRC)))

CFLAGS = -Wall -Werror
CFLAGS += -I $(SDKDIR)/FunSDK

.PHONY: all
all: code $(BUILD)/$(LIB_HCI)

.PHONY: code
code:
	../generator.py -p -g code -o fun_hci fun_hci.gen

.PHONY: doc
doc:
	../generator.py -p -g html -o fun_hci fun_hci.gen

$(BUILD)/obj/fun_hci.o: fun_hci.c
	@echo CC $<
	@mkdir -p `dirname $@`
	$(CC) -o $@ $(CFLAGS) -c $<

$(BUILD)/$(LIB_HCI): $(HCI_OBJS)
	$(AR) rcs $(BUILD)/$(LIB_HCI) $(HCI_OBJS)

.PHONY: install
install: $(BUILD)/$(LIB_HCI)
	mkdir -p $(SDKDIR)/FunSDK/hci/lib/$(LIBDST)/libfunhci.a
	cp $(BUILD)/$(LIB_HCI) $(SDKDIR)/FunSDK/hci/lib/posix/$(OS)/
	cp $(HCI_HDR) $(SDKDIR)/FunSDK/hci/include

.PHONY: clean
clean:
	rm -f fun_hci.c fun_hci.h
	rm  -rf $(BUILD)
