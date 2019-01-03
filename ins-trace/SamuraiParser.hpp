
class InstructionBuilder {
	InsReceiver<Ins> *_out;
	string _pending;

public:
	InstructionBuilder(InsReceiver<Ins> *out)
	: _out(out)
	{
	}

	void accept(const string& line)
	{
		if (line[0] == 'G') {
			assert(_pending.length() && _pending[0] == 'I');

			u64 cycle;
			u64 pc;
			parse_issue(_pending, &cycle, &pc);

			int reg_num;
			u64 reg_value;
			parse_graduate(line, &reg_num, &reg_value);

			_out->accept(Ins(cycle, pc, reg_num, reg_value));
			_pending = "";

		} else if (line[0] == 'I') {

			if (_pending.length() == 0) {
				_pending = line;
				return;
			}

			u64 cycle;
			u64 pc;
			parse_issue(_pending, &cycle, &pc);
			_out->accept(Ins(cycle, pc, 0, 0));
			_pending = line;
		} else {
			assert_msg(false, "%s", line.c_str());
		}
	}

	void finish()
	{
		_out->finish();
	}

private:
	void parse_issue(const string &line, u64 *cycle, u64 *pc)
	{
		assert(line[4] == ' ');
		assert(line[21] == ' ');
		*pc = IntParse::hex_fixed(line.c_str()+5, 16);
		assert(line.substr(39, 8) == "# Cycle=");
		*cycle = IntParse::decimal_till(line.c_str()+47, ' ');
	}

	void parse_graduate(const string &line, int *reg_num, u64 *reg_value)
	{
		const char *str = line.c_str();
		assert(str[4] == ' ');
		assert(str[21] == ' ');
		assert(str[18] == ' ');
		if (str[19] == ' ')
			*reg_num = IntParse::decimal_till(str+20, ' ');
		else
			*reg_num = IntParse::decimal_till(str+19, ' ');
		assert(0 <= *reg_num && *reg_num < 32);
		if (*reg_num)
			*reg_value = IntParse::hex_fixed(str+22, 16);
		else
			*reg_value = 0;
	}
};

class SamuraiParser {
public:
	void run(const char *path,
		 InsReceiver<Ins> *vp0,
		 InsReceiver<Ins> *vp1,
		 InsReceiver<Ins> *vp2,
		 InsReceiver<Ins> *vp3)
	{
		TextReader reader(path);

		bool vp_enabled[4] = { vp0 != 0, vp1 != 0, vp2 != 0, vp3 != 0};
		InstructionBuilder builders[4] = { vp0, vp1, vp2, vp3};

		string line_str;

		while (reader.get_line(line_str)) {
			int len = line_str.length();
			const char *line = line_str.c_str();
			if (line[0] == 'F') {
				assert(line[1] == ' ');
				continue;
			}
			if (line[0] == 'M') {
				assert(line[1] == 'H');
				assert(line[2] == ' ');
				continue;
			}
			assert(line[0] == 'I' || line[0] == 'G');
			assert_msg(line[1] == ' ', "line=%s", line);
			assert(line[2] == ' ');

			int vp = line[3] - '0';
			assert(0 <= vp && vp < 4);
			if (!vp_enabled[vp])
				continue;

			builders[vp].accept(line);
		}

		for (int i = 0; i < 4; i++)
			if (vp_enabled[i])
				builders[i].finish();
	}
};
