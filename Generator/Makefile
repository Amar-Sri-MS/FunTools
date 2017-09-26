# Where build products go.
BUILD = build

test: c-checker generator-test c-packed-checker html-checker fun-hci

# All tests for the Python generator script.
generator-test:
	python codegen_test.py
	python generator_test.py
	python htmlgen_test.py
	python utils_test.py
	python parser_test.py

# Tests generated C code compiles correctly.
c-checker: $(BUILD)
	./generator.py -g code -o $(BUILD)/rdma_gen examples/rdma.gen
	gcc -o rdma -g -I$(BUILD) -DDEBUG -DGENERATOR_TEST \
                test_helper/rdma.c $(BUILD)/rdma_gen.c
	./rdma

# Tests generated code with packed fields compiles correctly.
c-packed-checker: $(BUILD)
	./generator.py --codegen pack -g code -o \
                       $(BUILD)/rdma_packed_gen examples/rdma.gen
	gcc -o $(BUILD)/rdma_packed -g -I$(BUILD) -DDEBUG -DGENERATOR_TEST \
            test_helper/rdma_packed.c $(BUILD)/rdma_packed_gen.c

fun-hci: $(BUILD)
	./generator.py -g code -o $(BUILD)/fun_hci funhci/fun_hci.gen
	./generator.py -g html -o $(BUILD)/fun_hci funhci/fun_hci.gen
	./generator.py -g code -c pack,json -o $(BUILD)/fun_hci_pack funhci/fun_hci.gen
	./generator.py -g html -c pack,json -o $(BUILD)/fun_hci_pack funhci/fun_hci.gen
	
# Tests HTML generation works.
html-checker: $(BUILD)
	./generator.py -g html -o $(BUILD)/rdma-gen.html examples/rdma.gen

$(BUILD): $(BUILD)
	mkdir $(BUILD)
clean:
	@rm generator.pyc rdma rdma.dSYM rdma_packed rdma_packed.dSYM \
	    rdma.h rdma rdma_gen.[hc] rdma_packed_gen.[hc]
