
class DasmFunction {
public:
	const string name;
	const u64 start;
	const u64 len;

	DasmFunction(const string &name, u64 start, u64 len)
	: name(name), start(start), len(len)
	{
		assert(start % 4 == 0);
		assert_msg(len % 4 == 0, "%s", name.c_str());
	}
};

class DasmFile {

	vector<DasmFunction> _funcs;
	unordered_map<u64, DasmLine> _addr_to_dasm;
	DasmLine unknown;

public:
	DasmFile(const char *path)
		: unknown(~0ul, ~0, "unknown")
	{
		TextReader reader(path);

		/* Functions at or above 0xFFFFFFFF80000000 */
		vector<DasmFunction> funcs_ff;

		string func_name;
		u64 func_start = 0;

		u64 last_addr = 0;

		string line_str;

		while (reader.get_line(line_str)) {
			int len = line_str.length();
			const char *line = line_str.c_str();

			if (len == 0)
				continue;
			if (strncmp(line, "ffffffff", 8) &&
			    strncmp(line, "a8000000", 8) &&
			    strncmp(line, "a8000200", 8)) {
				if (strstr(line, "file format"))
					continue;
				if (!strncmp(line,
					     "Disassembly of section",
					     sizeof("Disassembly of section")-1))
					continue;
				assert_msg(0, "line=%s", line);
			}

			assert(len >= 16);
			u64 addr = hex_parse(line, 16);

			//printf("addr=%lx %s\n", addr, line);

			if (line[16] == ':') {
				assert(func_name.length());
				assert_msg(addr == last_addr+4, "addr=%lx last_addr=%lx", addr, last_addr);

				assert(len >= 28);
				assert(line[17] == '\t');

				u32 opcode = hex_parse(line+18, 8);
				assert(line[26] == ' ');
				assert_msg(line[27] == '\t', "line=%s", line);

				const char *asm_text = line+28;

				_addr_to_dasm.insert(std::make_pair(addr, DasmLine(addr, opcode, asm_text)));
				last_addr = addr;
			} else {
				assert(line[16] == ' ');
				assert(line[17] == '<');
				assert(line[len-2] == '>');
				assert(line[len-1] == ':');

				string name = string(line).substr(18, len-18-2);
				if (name[0] == '.' || name[0] == '$')
					continue;

				if (func_name.length()) {
					vector<DasmFunction> *funcs_ptr;

					if (func_start >= 0xFFFFFFFF80000000)
						funcs_ptr = &funcs_ff;
					else
						funcs_ptr = &_funcs;

					assert(funcs_ptr->size() == 0 ||
					       (*funcs_ptr)[funcs_ptr->size()-1].start < func_start);
					funcs_ptr->push_back(DasmFunction(func_name, func_start, addr - func_start));
				}

				func_name = string(line).substr(18, len-18-2);
				assert(func_name.length());
				func_start = addr;
				last_addr = addr - 4;
			}
		}

		for (int i = 0; i < funcs_ff.size(); i++)
			_funcs.push_back(funcs_ff[i]);
	}

	const DasmLine& lookup(u64 addr) const
	{
		auto it = _addr_to_dasm.find(addr);
		if (it != _addr_to_dasm.end())
			return it->second;

		if (0xFFFFFFFFA0000000 <= addr && addr < 0xFFFFFFFFC0000000) {
			u64 alias = addr - 0x20000000;
			it = _addr_to_dasm.find(alias);
			assert_msg(it != _addr_to_dasm.end(), "alias=%lx", alias);
			return it->second;
		}

		return unknown;
	}

	const DasmFunction& lookup_func(u64 addr) const
	{
		DasmFunction value("", addr, 0);

		auto ret = lower_bound(_funcs.cbegin(), _funcs.cend(), value,
			[](const DasmFunction& lhs, const DasmFunction& rhs) {
				assert(rhs.len == 0);
				return lhs.start + lhs.len <= rhs.start;
			});
		assert_msg(ret->start <= addr, "ret->start=%lx addr=%lx",
			   ret->start, addr);
		assert(ret->start+ret->len > addr);
		return *ret;
	}

	const DasmFunction lookup_func(const string& name) const
	{
		for (auto i : _funcs) {
			if (i.name == name)
				return i;
		}
		assert_msg(0, "%s", name.c_str());
	}
private:

	u64 hex_parse(const char *str, int len)
	{
		u64 value = 0;

		for (int i=0; i < len; i++) {
			value <<= 4;
			if (str[i] > '9') {
				assert('a' <= str[i] && str[i] <= 'f');
				value += str[i] - 'a' + 10;
			} else {
				assert('0' <= str[i] && str[i] <= '9');
				value += str[i] - '0';
			}
		}
		return value;
	}
};
