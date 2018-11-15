#include "Headers.hpp"

class Check : public InsReceiver<Ins>
{
	InsAsmBranchContext last_ins;

	enum InsType {
		Init = 0,
		Regular = 1,
		BranchWithoutDelay = 2,
		BranchWithDelay = 3,
		DelaySlotInstruction = 4,
	} last_ins_type = Init;

	u64 branch_target;
	DasmFile *dasm_file;
	RegContext context;
	unordered_map<u64,u64> stack_map;
public:
	Check(DasmFile *dasm_file)
	: dasm_file(dasm_file)
	{
	}

	void accept(const Ins &ins)
	{
		const DasmLine &dasm_line = dasm_file->lookup(ins.pc);
		InsAsmBranchContext ins_asm(ins, dasm_line, &context);

		InsAsmBranchContext born;
		while (!accept_check(ins_asm, born)) {
			InsAsmBranchContext dummy;
			bool ret = accept_check(born, dummy);
			assert(ret);
			info("%ld: %016lx  %s [[[BORN INS]]]", born.cycle, born.pc, born.op.text.c_str());
			if (born.reg_num)
				context.set(born.reg_num, born.reg_value);
			accept_stack(born);
			ins_asm = InsAsmBranchContext(ins, dasm_line, &context);
		}
		//info("%ld: %016lx  %s", ins_asm.cycle, ins_asm.pc, ins_asm.op.text.c_str());
		if (ins_asm.reg_num)
			context.set(ins_asm.reg_num, ins_asm.reg_value);
		accept_stack(ins_asm);
	}

	bool accept_check(const InsAsmBranchContext &ins, InsAsmBranchContext &born)
	{
		//info("last_ins_type=%d ins_type=%d", last_ins_type, ins_type);

		bool delay_slot_ins = false;

		if (last_ins_type == Init) {
			assert(ins.pc == 0xffffffffa0100000);
		} else if (last_ins_type == Regular) {
			if (ins.pc != last_ins.pc + 4) {
				error("Handle missing instruction:");
				const DasmLine &dasm_line = dasm_file->lookup(last_ins.pc + 4);
				error("?: %016lx  %s", dasm_line.addr, dasm_line.op.text.c_str());
				born = Repair::missing_instruction(dasm_line, last_ins.cycle, context, stack_map);
				return false;
			}
		} else if (last_ins_type == BranchWithoutDelay) {
			if (last_ins.op.type() == "eret") {
				// TODO: can this be fixed?
				assert(branch_target == 0);
			} else {
				if (ins.pc != branch_target) {
					error("Handle missing instruction at non-delayed branch target:");
					const DasmLine &dasm_line = dasm_file->lookup(branch_target);
					error("?: %016lx  %s", dasm_line.addr, dasm_line.op.text.c_str());
					born = Repair::missing_instruction(dasm_line, last_ins.cycle, context, stack_map);
					return false;
				}
			}
		} else if (last_ins_type == BranchWithDelay) {
			assert(ins.pc == last_ins.pc + 4);
			delay_slot_ins = true;
		} else {
			assert(last_ins_type == DelaySlotInstruction);
			if (ins.pc != branch_target) {
				if (ins.pc == branch_target+4) {
					error("Single missing instruction after delayed jump:");
					const DasmLine &dasm_line = dasm_file->lookup(branch_target);
					born = Repair::missing_instruction(dasm_line, last_ins.cycle, context, stack_map);
					return false;
				} else {
					assert_msg(ins.pc == branch_target,
						  "pc=%lx branch_target=%lx",
						  ins.pc, branch_target);
				}
			}
		}


		branch_target = 0;

		if (ins.taken_branch) {
			assert(delay_slot_ins == false);
			if (ins.has_delay_slot) {
				last_ins_type = BranchWithDelay;
			} else {
				last_ins_type = BranchWithoutDelay;
				branch_target = ins.branch_target;
			}
		} else {
			if (delay_slot_ins) {
				last_ins_type = DelaySlotInstruction;
				branch_target = last_ins.branch_target;
			} else {
				last_ins_type = Regular;
			}
		}
		last_ins = ins;
		return true;
	}

	void accept_stack(const InsAsmBranchContext &ins)
	{
		const string& type = ins.op.type();

		bool store = (type == "sd");
		if (!store && ins.op.type() != "ld")
			return;

		string reg, offset, mem_reg, empty;
		String::split_into_4(ins.op.arg(), ",()", &reg, &offset, &mem_reg, &empty);
		assert(empty.length() == 0);

		u64 mem_addr = context.get(mem_reg) + IntParse::signed_decimal(offset);
		u64 sp = context.get("sp");

		if (store) {
#if 0
			if (mem_addr < sp - 4096) {
				//info("mem_addr=%016lx far below stack=%016lx", mem_addr, sp);
				return;
			}

			if (mem_addr > sp - 64*1024) {
				//info("mem_addr=%016lx far above stack=%016lx", mem_addr, sp);
				return;
			}
#endif
			u64 value = context.get(reg);

			//info("Stack write: [%016lx] <-- %016lx  %s", mem_addr, value, ins.op.text.c_str());
			stack_map[mem_addr] = value;
		} else {
			auto it = stack_map.find(mem_addr);
			if (it == stack_map.end()) {
				if (mem_reg == "sp")
					error("mem_addr=%016lx does not exist", mem_addr);
				return;
			}

			u64 map_value = it->second;

			//info("Stack read: [%016lx] has %016lx (%016lx reg_value)  %s", mem_addr, map_value, ins.reg_value, ins.op.text.c_str());
			assert(reg == RegNames::get(ins.reg_num));

			if (map_value != ins.reg_value)
				error("Stack map mismatch map_value=%lx reg_value=%lx", map_value, ins.reg_value);
		}
	}
};

class RegContextAdder : public InsReceiver<Ins>
{
	InsReceiver<InsAsmBranchContext> &_out;
	const DasmFile &_dasm_file;
	RegContext *context;
public:
	RegContextAdder(const DasmFile& dasm_file,
			RegContext *context,
			InsReceiver<InsAsmBranchContext> *out)
	: _dasm_file(dasm_file), context(context), _out(*out)
	{
	}

	void accept(const Ins &ins)
	{
		InsAsmBranchContext out_ins(ins, _dasm_file.lookup(ins.pc), context);

		_out.accept(out_ins);

		if (ins.reg_num) {
			context->set(ins.reg_num, ins.reg_value);
		}
	}
};


int main(int argc, char const *argv[])
{
	assert(argc == 3 && "Usage: ./check dasm-file trace-file");

	DasmFile dasm_file(argv[1]);
	Check check(&dasm_file);
	//PrintSeparator separator(&check);
	Decoder(argv[2], &check).run();

	return 0;
}
