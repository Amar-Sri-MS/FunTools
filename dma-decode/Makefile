SOURCES :=	main.c

HEADERS :=	decode.h \
		data-type-def.h \
		data-type-def-action.h \
		data-type-def-arg0.h \
		data-type-def-arg1.h \
		data-type-def-cmd-common.h \
		data-type-def-cmd-gather.h \
		data-type-def-cmd-scatter.h \
		data-type-def-cmd.h

all: dma-decode

dma-decode:  $(SOURCES) $(HEADERS)
	gcc -o $@ $(SOURCES)

clean:
	rm -f *.o
	rm -f *~
	rm -f dma-decode
