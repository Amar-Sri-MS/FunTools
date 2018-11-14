#include "Headers.hpp"

class RawPrint : public InsReceiver<Ins>
{
	u64 last_cycle;
	u64 cycle_from;
	u64 cycle_to;
public:
	RawPrint(u64 cycle_from, u64 cycle_to)
	:cycle_from(cycle_from), cycle_to(cycle_to)
	{
	}

	void accept(const Ins &ins)
	{
		if (cycle_from <= ins.cycle && ins.cycle <= cycle_to) {
			if (ins.reg_num)
				info("%ld: %016lx  %s <- 0x%016lx", ins.cycle,
				     ins.pc, RegNames::get(ins.reg_num).c_str(),
				     ins.reg_value);
			else
				info("%ld: %016lx", ins.cycle, ins.pc);
		}
		last_cycle = ins.cycle;
	}

	void finish()
	{
		info("last_cycle=%ld", last_cycle);
	}
};

int main(int argc, char const *argv[])
{
	assert_msg(argc >= 2, "Usage: %s trace-file [start-cycle] [end-cycle]",
		   argv[0]);

	u64 cycle_from = 0;
	u64 cycle_to = ~0;
	if (argc > 2)
		cycle_from = IntParse::decimal(argv[2]);
	if (argc > 2)
		cycle_to = IntParse::decimal(argv[3]);

	RawPrint print(cycle_from, cycle_to);

	Decoder(argv[1], &print).run();

	return 0;
}
