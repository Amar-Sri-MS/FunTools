#include "Headers.hpp"

class CallFrame
{
public:
	const DasmFunction& func;
	const u64 ret_pc;

	CallFrame(const DasmFunction& func, u64 ret_pc)
	:func(func), ret_pc(ret_pc)
	{
	}
};

class Graph : public InsReceiver<Ins>
{
	const DasmFile &dasm_file;
	vector<Ins> ins_hist;
	stack<CallFrame> call_stack;
	bool filter_on = false;
	int filter_depth;


public:
	Graph(DasmFile *dasm_file)
	: dasm_file(*dasm_file)
	{
	}

	void accept(const Ins &ins)
	{
		auto const& dasm_line = dasm_file.lookup(ins.pc);
		//info("%016lx %s", ins.pc, dasm_line.op.text.c_str());

		auto const& func = dasm_file.lookup_func(ins.pc);

		if (ins_hist.size() < 2)
			goto skip;

		if (ins.pc == func.start) {
			u64 last_pc = ins_hist[1].pc;
			auto const& last_dasm_line = dasm_file.lookup(last_pc);
			const string& last_op = last_dasm_line.op.type();

			u64 prev2_pc = ins_hist[0].pc;
			auto const& prev2_dasm_line = dasm_file.lookup(prev2_pc);
			const string& prev2_op = prev2_dasm_line.op.type();

			int prev_stack_size = call_stack.size();
			if (last_op == "balc" ||
			    last_op == "jalrc") {
				call_stack.push(CallFrame(func, last_pc+4));
			} else if (prev2_op == "jalr") {
				assert(prev2_pc+4 == last_pc);
				call_stack.push(CallFrame(func, prev2_pc+8));
			} else if (last_op == "bc" || last_op == "bnezc") {
			} else {
				assert_msg(0, "last_op=%s prev2_op=%s", last_op.c_str(), prev2_op.c_str());
			}

			if (!filter_on && call_stack.size() != prev_stack_size) {
				info("%*s", (int)call_stack.size(), "\\");
				info("%*s", (int)call_stack.size()+(int)func.name.length(), func.name.c_str());
				if (func.name == "printf") {
					filter_on = true;
					filter_depth = call_stack.size();
				}
			}
		} else if (call_stack.size() > 0 && ins.pc == call_stack.top().ret_pc) {
			if (filter_on && filter_depth == call_stack.size()) {
				filter_on = false;
			}
			if (!filter_on) {
				int indent = call_stack.size();
				info("%*s", indent + (int)call_stack.top().func.name.length(), call_stack.top().func.name.c_str());
				info("%*s", (int)call_stack.size(), "/");
			}
			call_stack.pop();
		}

	skip:
		if (ins_hist.size() == 2)
			ins_hist.erase(ins_hist.begin());
		ins_hist.push_back(ins);
	}
};

class FilterUntil : public InsReceiver<Ins>
{
	InsReceiver<Ins>& out;
	u64 pc;
	bool seen;
public:
	FilterUntil(u64 pc, InsReceiver<Ins> *out)
	: pc(pc), out(*out)
	{
	}

	void accept(const Ins &ins)
	{
		if (!seen) {
			if (ins.pc != pc)
				return;
			seen = true;
		}

		out.accept(ins);
	}

};
int main(int argc, char const *argv[])
{
	assert(argc == 3 && "Usage: ./graph dasm-file trace-file");

	DasmFile dasm_file(argv[1]);

	Graph graph(&dasm_file);
	Decoder(argv[2], &graph).run();

	return 0;
}
