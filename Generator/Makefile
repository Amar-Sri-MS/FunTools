test: c-checker generator-test c-packed-checker

generator-test:
	python generator_test.py
	python codegen_test.py

c-checker:
	./generator.py -g code -o rdma.h examples/rdma.gen
	gcc -o rdma -g -I. test_helper/rdma.c
	./rdma

c-packed-checker:
	./generator.py -p -g code -o rdma_packed.h examples/rdma.gen
	gcc -o rdma_packed -g -I. test_helper/rdma_packed.c
	./rdma_packed

clean:
	rm generator.pyc rdma rdma.dSYM rdma_packed rdma_packed.dSYM
	rm rdma.h rdma
