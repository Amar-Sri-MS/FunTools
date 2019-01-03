
class Ins {
public:
	u64 cycle;
	u64 pc;
	u64 reg_num;
	u64 reg_value;

	Ins(u64 cycle, u64 pc, u64 reg_num, u64 reg_value)
	 : cycle(cycle), pc(pc), reg_num(reg_num), reg_value(reg_value)
	{
		assert(reg_num < 32);
		assert(reg_num > 0 || reg_value == 0);
	}

	Ins(const Ins &ins)
	: Ins(ins.cycle, ins.pc, ins.reg_num, ins.reg_value)
	{
	}

	Ins(){}
};

class InsAsm : public Ins {
public:
	const Op &op;

	InsAsm(const Ins &ins, const DasmLine &dasm_line)
	: Ins(ins), op(dasm_line.op)
	{
	}
};

class InsAsmBranchContext : public Ins {
public:
	bool taken_branch;
	bool has_delay_slot;
	u64 branch_target;
	Op op;

	InsAsmBranchContext(const Ins &ins, const DasmLine &dasm_line, const RegContext *context)
	: Ins(ins), op(dasm_line.op)
	{
		string type = op.type();

		if (!OpType::is_branch(type, &has_delay_slot)) {
			taken_branch = false;
			has_delay_slot = false;
			branch_target = 0;
		} else {
			u64 reloc = ins.pc - dasm_line.addr;
			taken_branch = Branch::is_taken(type, op.arg(),
							reloc, context, &branch_target);
		}

		//info("%ld: %lx %s tb=%d hds=%d bt=%lx", ins.cycle, ins.pc, dasm_line.asm_text.c_str(), taken_branch, has_delay_slot, branch_target);
	}

	InsAsmBranchContext()
	: op("")
	{}
};
