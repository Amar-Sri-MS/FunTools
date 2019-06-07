#include "Headers.hpp"

class FindMemWriter : public InsReceiver<Ins>
{
	DasmFile *dasm_file;
	RegContext context;
	u64 mem_address;
	u64 mem_size;
public:
	FindMemWriter(DasmFile *dasm_file, u64 mem_address, u64 mem_size)
	: dasm_file(dasm_file), mem_address(mem_address), mem_size(mem_size)
	{
	}

	void accept(const Ins &ins)
	{
		process(ins);
		if (ins.reg_num)
			context.set(ins.reg_num, ins.reg_value);
	}

private:
	void process(const Ins &ins)
	{

		const DasmLine &dasm_line = dasm_file->lookup(ins.pc);

		u64 write_size;

		if (dasm_line.op.type() == "sd")
			write_size = 8;
		else if(dasm_line.op.type() == "sw")
			write_size = 4;
		else if (dasm_line.op.type() == "sh")
			write_size = 2;
		else if (dasm_line.op.type() == "sb")
			write_size = 1;
		else
			return;

		string arg = dasm_line.op.arg();
		string reg, offset, base_reg, empty;

		String::split_into_4(arg, ",()", &reg, &offset, &base_reg, &empty);
		assert(empty.length() == 0);

		u64 addr = IntParse::signed_decimal(offset) + context.get(base_reg);

		if (addr + write_size <= mem_address || mem_address + mem_size <= addr)
			return;

		string text;
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

		info("%ld: %016lx  %s\t%s", ins.cycle, ins.pc, String::pad(dasm_line.op.type(), INS_MAX_STR_LEN).c_str(), text.c_str());
	}
};


int main(int argc, char const *argv[])
{
	assert_msg(argc == 5,
		   "Usage: %s dasm-file trace-file addr size",
		   argv[0]);

	const char *addr = argv[3];
	if (addr[0] == '0' && addr[1] == 'x')
		addr += 2;
	u64 mem_address = IntParse::hex_16(addr);
	u64 mem_size = IntParse::hex(argv[4]);

	DasmFile dasm_file(argv[1]);
	FindMemWriter writer(&dasm_file, mem_address, mem_size);
	Decoder(argv[2], &writer).run();
	return 0;
}
