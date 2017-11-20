# Makefile for Fungible header generator.

# Location of FunSDK - so we can test with real fun_hci file.
FUNSDK_INSTALL_DIR = ../../FunSDK/bin/Generator
FUN_HCI_DIR = ../../FunSDk/FunSDK/hci

# Where build products go.
BUILD = build

GENERATOR_SRC = generator.py \
		codegen.py \
		htmlgen.py \
		parser.py \
		utils.py \
		header.tmpl \
		source.tmpl

test: generator-test test_rdma test_rdma_packed test_rdma_html
test: test_swap test_simple_validation

# Test new generator with actual fun-hci file in the future.  For now,
# it complicates configuring Jenkins.
# test: fun-hci

# All tests for the Python generator script.
generator-test:
	python codegen_test.py
	python generator_test.py
	python htmlgen_test.py
	python utils_test.py
	python parser_test.py

fun-hci: $(BUILD)
	./generator.py -g code -o $(BUILD)/fun_hci $(FUN_HCI_DIR)/fun_hci.gen
	./generator.py -g html -o $(BUILD)/fun_hci $(FUN_HCI_DIR)/fun_hci.gen
	./generator.py -g code -c pack,json -o $(BUILD)/fun_hci_pack $(FUN_HCI_DIR)/fun_hci.gen
	./generator.py -g html -c pack,json -o $(BUILD)/fun_hci_pack $(FUN_HCI_DIR)/fun_hci.gen


# Tests generated C code compiles correctly.
test_rdma: $(BUILD)
	./generator.py -g code -o $(BUILD)/rdma_gen examples/rdma.gen
	gcc -o rdma -g -I$(BUILD) -DDEBUG -DGENERATOR_TEST \
                test_helper/rdma.c $(BUILD)/rdma_gen.c
	./rdma

# Tests generated code with packed fields compiles correctly.
test_rdma_packed: $(BUILD)
	./generator.py --codegen pack -g code -o \
                       $(BUILD)/rdma_packed_gen examples/rdma.gen
	gcc -o $(BUILD)/rdma_packed -g -I$(BUILD) -DDEBUG -DGENERATOR_TEST \
            test_helper/rdma_packed.c $(BUILD)/rdma_packed_gen.c

test_swap: test_helper/swap.c examples/swap.gen
	./generator.py -g code --codegen pack,swap -o $(BUILD)/swap_gen examples/swap.gen
	gcc -o $(BUILD)/swap -g -I$(BUILD) -DDEBUG -DGENERATOR_TEST \
	test_helper/swap.c $(BUILD)/swap_gen.c
	$(BUILD)/swap

# Tests HTML generation works.
test_rdma_html: examples/rdma.gen $(GENERATOR_SRC)
	./generator.py -g html -o $(BUILD)/rdma-gen examples/rdma.gen

test_simple_validation: examples/simple.gen $(GENERATOR_SRC)
	./generator.py -g validate -o $(BUILD)/simple_gen examples/simple.gen
	gcc -o $(BUILD)/simple_gen.validate $(BUILD)/simple_gen.validate.c
	$(BUILD)/simple_gen.validate

$(BUILD): $(BUILD)
	mkdir $(BUILD)

# install generator to SDK
install:
	mkdir -p $(FUNSDK_INSTALL_DIR)
	rsync -R $(GENERATOR_SRC) $(FUNSDK_INSTALL_DIR)


clean:
	@rm -rf *.pyc */*.pyc rdma rdma.dSYM rdma_packed rdma_packed.dSYM \
	    rdma.h rdma rdma_gen.[hc] rdma_packed_gen.[hc]
