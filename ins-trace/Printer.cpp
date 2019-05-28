#include "Headers.hpp"

class Printer : public InsReceiver<InsAsm>
{
	u64 last_cycle;
	u64 cycle_from;
	u64 cycle_to;
public:
	Printer(u64 cycle_from, u64 cycle_to)
	:cycle_from(cycle_from), cycle_to(cycle_to)
	{
	}

	void accept(const InsAsm &ins)
	{
		if (cycle_from <= ins.cycle && ins.cycle <= cycle_to)
			info("%ld: %016lx  %s\t%s", ins.cycle, ins.pc, String::pad(ins.op.type(), INS_MAX_STR_LEN).c_str(), ins.op.arg().c_str());

		last_cycle = ins.cycle;
	}

	void finish()
	{
		info("last_cycle=%ld", last_cycle);
	}
};

int main(int argc, char const *argv[])
{
	assert_msg(argc >= 3,
		   "Usage: %s dasm-file trace-file [start-cycle [end-cycle]]",
		   argv[0]);

	u64 cycle_from = 0;
	u64 cycle_to = ~0;
	if (argc > 3)
		cycle_from = IntParse::decimal(argv[3]);
	if (argc > 4)
		cycle_to = IntParse::decimal(argv[4]);

	Printer printer(cycle_from, cycle_to);

	DasmFile dasm_file(argv[1]);
	InsDecorator<InsAsm> decorator(dasm_file, &printer);

	Decoder(argv[2], &decorator).run();

	return 0;
}
