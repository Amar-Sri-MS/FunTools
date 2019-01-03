#include "Headers.hpp"

class LatencyStats {
	u64 min_cycles;
	u64 max_cycles;
	u64 count;
	u64 total;

public:
	void accept(u64 latency)
	{
		if (min_cycles == 0 || latency < min_cycles)
			min_cycles = latency;

		if (max_cycles == 0 || latency > max_cycles)
			max_cycles = latency;

		count++;
		total += latency;
		assert(total >= latency);
	}

	void finish()
	{
		info("min_cycles = %ld", min_cycles);
		info("max_cycles = %ld", max_cycles);
		info("count = %ld", count);
		if (count)
			info("average = %ld", total/count);
	}
};

class Latency : public InsReceiver<Ins>
{
	u64 from_pc, to_pc;
	const DasmFile &dasm_file;
	u64 start_cycle;

	LatencyStats out;
public:
	Latency(u64 from_pc, u64 to_pc, DasmFile *dasm_file)
	: from_pc(from_pc), to_pc(to_pc), dasm_file(*dasm_file)
	{
	}

	void accept(const Ins &ins)
	{
		if (start_cycle == 0 && ins.pc != from_pc)
			return;

		auto const& dasm_line = dasm_file.lookup(ins.pc);
		info("%ld: %016lx %s", ins.cycle, ins.pc, dasm_line.op.text.c_str());

		if (start_cycle == 0) {
			start_cycle = ins.cycle;
		} else {
			if (ins.pc == to_pc) {
				info("%ld: %016lx delta %ld", ins.cycle, ins.pc, ins.cycle - start_cycle);
				out.accept(ins.cycle - start_cycle);
				start_cycle = 0;
			}
		}
	}

	void finish()
	{
		out.finish();
	}
};

int main(int argc, char const *argv[])
{
	assert(argc == 5 && "Usage: ./latency dasm-file trace-file from_pc to_pc");

	DasmFile dasm_file(argv[1]);
	Latency latency(IntParse::hex_16(argv[3]), IntParse::hex_16(argv[4]), &dasm_file);
	Decoder(argv[2], &latency).run();

	return 0;
}
