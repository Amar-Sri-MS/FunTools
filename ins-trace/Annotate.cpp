#include "Headers.hpp"

class Annotate : public InsReceiver<Ins>
{
	DasmFile *dasm_file;
	RegContext context;
	u64 cycle_from;
	u64 cycle_to;
public:
	Annotate(DasmFile *dasm_file, u64 cycle_from, u64 cycle_to)
	: dasm_file(dasm_file), cycle_from(cycle_from), cycle_to(cycle_to)
	{
	}

	void accept(const Ins &ins)
	{
		if (cycle_from <= ins.cycle && ins.cycle <= cycle_to)
			print(ins);
		if (ins.reg_num)
			context.set(ins.reg_num, ins.reg_value);
	}

private:
	void print(const Ins &ins)
	{
		const DasmLine &dasm_line = dasm_file->lookup(ins.pc);

		string text;
		string arg = dasm_line.op.arg();

		bool reg_write_seen = false;
		do {
			string token;
			if (arg.find(',') != arg.npos) {
				string rest;
				String::split_into_2(arg, ',', &token, &rest);
				arg = rest;
			} else {
				token = arg;
				arg = "";
			}

			string prefix;
			string reg;
			string suffix;
			if (token.find('(') != token.npos) {
				String::split_into_3(token, "()", &prefix, &reg, &suffix);
				prefix += "(";
				assert(suffix.length() == 0);
				suffix = ")";
			} else {
				reg = token;
			}

			text += prefix;

			if (RegNames::is_reg_name(reg) && reg != "zero") {
				text += reg;
				if (!reg_write_seen && RegNames::get(reg) == ins.reg_num) {
					text += "=" + String::to_hex_16(ins.reg_value);
					reg_write_seen = true;
				} else {
					text += ":" + String::to_hex_16(context.get(reg));
				}
			} else {
				text += reg;
			}

			text += suffix;
			if (arg.length())
				text += " ";

		} while (arg.length());

		info("%ld: %016lx  %s\t%s", ins.cycle, ins.pc, String::pad(dasm_line.op.type(), 10).c_str(), text.c_str());
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

	DasmFile dasm_file(argv[1]);
	Annotate annotate(&dasm_file, cycle_from, cycle_to);
	//PrintSeparator separator(&check);
	Decoder(argv[2], &annotate).run();

	return 0;
}
