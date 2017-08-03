test: c-checker generator-test c-packed-checker html-checker

generator-test:
	python codegen_test.py
	python generator_test.py
	python htmlgen_test.py
	python utils_test.py

c-checker:
	./generator.py -g code -o rdma_gen examples/rdma.gen
	gcc -o rdma -g -I. -DDEBUG -DGENERATOR_TEST test_helper/rdma.c rdma_gen.c
	./rdma

c-packed-checker:
	./generator.py --codegen pack,json -g code -o rdma_packed_gen examples/rdma.gen
	gcc -o rdma_packed -g -I. -DDEBUG -DGENERATOR_TEST test_helper/rdma_packed.c rdma_packed_gen.c
	./rdma_packed

html-checker:
	./generator.py --codegen pack,json -g html -o rdma.html examples/rdma.gen

clean:
	rm generator.pyc rdma rdma.dSYM rdma_packed rdma_packed.dSYM
	rm rdma.h rdma rdma_gen.[hc] rdma_packed_gen.[hc]
