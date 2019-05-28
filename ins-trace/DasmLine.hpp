/* Longest instructions are sync_acquire/sync_release */
#define INS_MAX_STR_LEN 12

class Op {
public:
	string text;

	Op(const char *asm_text)
	: text(asm_text)
	{
	}

	string type() const
	{
		const char *str = text.c_str();
		const char *op_end = strchr(str, '\t');
		if (!op_end)
			return text;
		return text.substr(0, op_end - str);
	}

	string arg() const
	{
		const char *str = text.c_str();
		const char *op_end = strchr(str, '\t');
		if (!op_end)
			return "";
		return op_end+1;
	}
};

class DasmLine {
public:
	const u64 addr;
	const u32 opcode;
	Op op;

	DasmLine(u64 addr, u32 opcode, const char *asm_text)
	: addr(addr), opcode(opcode), op(asm_text)
	{
	}
};

