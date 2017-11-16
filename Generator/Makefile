# Where build products go.

SDKDIR ?= ../../FunSDK/FunSDK

BUILD = build

GENERATOR_SRC = generator.py \
		codegen.py \
		htmlgen.py \
		parser.py \
		utils.py \
		header.tmpl \
		source.tmpl

test: generator-test test_rdma test_rdma_packed test_rdma_html fun-hci
test: test_swap

# All tests for the Python generator script.
generator-test:
	python codegen_test.py
	python generator_test.py
	python htmlgen_test.py
	python utils_test.py
	python parser_test.py

fun-hci: $(BUILD)
	./generator.py -g code -o $(BUILD)/fun_hci $(SDKDIR)/hci/fun_hci.gen
	./generator.py -g html -o $(BUILD)/fun_hci $(SDKDIR)/hci/fun_hci.gen
	./generator.py -g code -c pack,json -o $(BUILD)/fun_hci_pack $(SDKDIR)/hci/fun_hci.gen
	./generator.py -g html -c pack,json -o $(BUILD)/fun_hci_pack $(SDKDIR)/hci/fun_hci.gen


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
test_rdma_html: $(BUILD)
	./generator.py -g html -o $(BUILD)/rdma-gen.html examples/rdma.gen

$(BUILD): $(BUILD)
	mkdir $(BUILD)

# install generator to SDK
install:
	mkdir -p $(SDKDIR)/bin/Generator
	rsync -R $(GENERATOR_SRC) $(SDKDIR)/bin/Generator


clean:
	@rm -rf *.pyc */*.pyc rdma rdma.dSYM rdma_packed rdma_packed.dSYM \
	    rdma.h rdma rdma_gen.[hc] rdma_packed_gen.[hc]
