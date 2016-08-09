tests: c-checker generator-test

generator-test:
	python generator-test.py

c-checker:
	./generator.py -g code -o rdma.h examples/rdma.gen
	gcc -o rdma -g -I. test_helper/rdma.c
	./rdma

clean:
	rm -r generator.pyc rdma rdma.dSYM rdma.o rdma.h
