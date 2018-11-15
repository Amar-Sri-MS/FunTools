class Repair
{
public:
	static InsAsmBranchContext missing_instruction(const DasmLine& dasm_line,
					u64 cycle,
					const RegContext& context,
					unordered_map<u64, u64>& stack_map)
	{
		u64 addr = dasm_line.addr;

		string type = dasm_line.op.type();

		if (type == "ld") {
			string reg, offset, src_reg, empty;
			String::split_into_4(dasm_line.op.arg(), ",()", &reg, &offset, &src_reg, &empty);
			assert(empty.length() == 0);

			u64 mem_addr = context.get(src_reg) + IntParse::signed_decimal(offset);
			assert(reg != "zero");
			Ins ins(cycle, addr, RegNames::get(reg), stack_map[mem_addr]);
			return InsAsmBranchContext(ins, dasm_line, &context);
		}

		if (type == "andi") {
			string reg1, reg2, zero, imm;
			String::split_into_4(dasm_line.op.arg(), ",,x", &reg1, &reg2, &zero, &imm);
			assert(zero == "0");
			assert(reg1 != "zero");
			Ins ins(cycle, addr, RegNames::get(reg1), context.get(reg2) & IntParse::hex(imm));
			return InsAsmBranchContext(ins, dasm_line, &context);;
		}

		if (type == "move") {
			string reg1, reg2;
			String::split_into_2(dasm_line.op.arg(), ',', &reg1, &reg2);
			assert(reg1 != "zero");
			Ins ins(cycle, addr, RegNames::get(reg1), context.get(reg2));
			return InsAsmBranchContext(ins, dasm_line, &context);;
		}

		if (type == "daddu") {
			string reg1, reg2, reg3;
			String::split_into_3(dasm_line.op.arg(), ",,", &reg1, &reg2, &reg3);
			assert(reg1 != "zero");
			Ins ins(cycle, addr, RegNames::get(reg1), context.get(reg2) + context.get(reg3));
			return InsAsmBranchContext(ins, dasm_line, &context);;
		}

		if (type == "balc") {
			Ins ins(cycle, addr, RegNames::get("ra"), addr+4);
			return InsAsmBranchContext(ins, dasm_line, &context);;
		}

		if (type == "daddiu") {
			string reg1, reg2, imm;
			String::split_into_3(dasm_line.op.arg(), ",,", &reg1, &reg2, &imm);
			assert(reg1 != "zero");
			Ins ins(cycle, addr, RegNames::get(reg1), context.get(reg2) + IntParse::signed_decimal(imm));
			return InsAsmBranchContext(ins, dasm_line, &context);;
		}

		if (type == "lui") {
			string reg1, zero, imm;
			String::split_into_3(dasm_line.op.arg(), ",x", &reg1, &zero, &imm);
			assert(zero == "0");
			assert(reg1 != "zero");
			u64 value = (long)(int)(IntParse::hex(imm) << 16);
			Ins ins(cycle, addr, RegNames::get(reg1), value);
			return InsAsmBranchContext(ins, dasm_line, &context);;
		}

		if (type == "bnezc" || type == "sync") {
			Ins ins(cycle, addr, 0, 0);
			return InsAsmBranchContext(ins, dasm_line, &context);;
		}

		assert(000);
	}
};
