#include "Headers.hpp"

int main(int argc, char const *argv[])
{
	assert(argc == 3 && "Usage: encode samurai-file out-prefix");

	string out = argv[2];

	TraceEncoder vp0((out + "-0.te").c_str());
	TraceEncoder vp1((out + "-1.te").c_str());
	TraceEncoder vp2((out + "-2.te").c_str());
	TraceEncoder vp3((out + "-3.te").c_str());

	SamuraiParser samurai_parser;

	samurai_parser.run(argv[1], &vp0, &vp1, &vp2, &vp3);
	return 0;
}
