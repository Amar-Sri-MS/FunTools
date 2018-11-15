HEADERS = $(wildcard *.hpp)

C++ = g++
CPP_FLAGS = -g -std=c++11 -DDEBUG=1 -O3

BUILD = ./build

$(BUILD)/annotate: Annotate.cpp Decoder.cpp OpType.cpp RegNames.cpp $(HEADERS)
	$(C++) $(CPP_FLAGS) $(filter-out $(HEADERS), $^) -o $@

$(BUILD)/check: Check.cpp Decoder.cpp OpType.cpp RegNames.cpp $(HEADERS)
	$(C++) $(CPP_FLAGS) $(filter-out $(HEADERS), $^) -o $@

$(BUILD)/encode: Encode.cpp $(HEADERS)
	$(C++) $(CPP_FLAGS) $(filter-out $(HEADERS), $^) -o $@

$(BUILD)/graph: Graph.cpp Decoder.cpp OpType.cpp RegNames.cpp $(HEADERS)
	$(C++) $(CPP_FLAGS) $(filter-out $(HEADERS), $^) -o $@

$(BUILD)/latency: Latency.cpp Decoder.cpp OpType.cpp RegNames.cpp $(HEADERS)
	$(C++) $(CPP_FLAGS) $(filter-out $(HEADERS), $^) -o $@

$(BUILD)/printer: Printer.cpp Decoder.cpp $(HEADERS)
	$(C++) $(CPP_FLAGS) $(filter-out $(HEADERS), $^) -o $@

$(BUILD)/raw-print: RawPrint.cpp Decoder.cpp RegNames.cpp $(HEADERS)
	$(C++) $(CPP_FLAGS) $(filter-out $(HEADERS), $^) -o $@

$(BUILD)/find-mem-writer: FindMemWriter.cpp Decoder.cpp OpType.cpp RegNames.cpp $(HEADERS)
	$(C++) $(CPP_FLAGS) $(filter-out $(HEADERS), $^) -o $@
