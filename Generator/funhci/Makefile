
# Platform
OS := $(shell uname)

MACHINE ?= posix
DEST ?= out

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

OUT_HCI = fun_hci
OUT_PORT = port_enum

HCI_SRC = $(OUT_HCI).c
HCI_HDR = $(OUT_HCI).h

HCI_OBJS = $(patsubst %.c,$(BUILD)/obj/%.o,$(filter %c,$(HCI_SRC)))

CFLAGS = -Wall -Werror
CFLAGS += -I $(SDKDIR)/FunSDK -I $(SDKDIR)

.PHONY: all
all: funos_code host_code funos_enum $(BUILD)/$(LIB_HCI)

.PHONY: funos_code
funos_code:
	@mkdir -p $(DEST)/funos
	../generator.py -c pack,json -g code -o $(DEST)/funos/$(OUT_HCI) fun_hci.gen

.PHONY: funos_enum
funos_enum:
	@mkdir -p $(DEST)/funos
	../generator.py -c pack -g code -o $(DEST)/funos/$(OUT_PORT) fun_port.gen

.PHONY: host_code
host_code:
	@mkdir -p $(DEST)/host
	../generator.py -c pack -g code -o $(DEST)/host/$(OUT_HCI) fun_hci.gen

.PHONY: doc
doc:
	@mkdir -p $(DEST)/doc
	../generator.py -g html -o $(DEST)/doc/$(OUT_HCI) fun_hci.gen
	../generator.py -g html -o $(DEST)/doc/$(OUT_PORT) fun_port.gen

$(BUILD)/obj/fun_hci.o: $(DEST)/funos/$(OUT_HCI).c
	@echo CC $<
	@mkdir -p `dirname $@`
	$(CC) -o $@ $(CFLAGS) -c $<

$(BUILD)/$(LIB_HCI): $(HCI_OBJS)
	$(AR) rcs $(BUILD)/$(LIB_HCI) $(HCI_OBJS)

.PHONY: install
install: $(BUILD)/$(LIB_HCI)
	mkdir -p $(SDKDIR)/FunSDK/hci/lib/$(LIBDST)
	mkdir -p $(SDKDIR)/FunSDK/hci/include
	cp $(BUILD)/$(LIB_HCI) $(SDKDIR)/FunSDK/hci/lib/$(LIBDST)/libfunhci.a
	cp $(DEST)/$(HCI_HDR) $(SDKDIR)/FunSDK/hci/include

.PHONY: clean
clean:
	rm -f $(DEST)/funos/*
	rm -f $(DEST)/host/*
	rm -f $(DEST)/doc/*
	rm  -rf $(BUILD)
