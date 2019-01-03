
class RegContext {

	bool valid[32];
	u64 regs[32];
public:
	RegContext()
	{
		valid[0] = true;
		regs[0] = 0;

		for (int i=1; i < 32; i++) {
			valid[i] = true;
			regs[i] = 0;
		}
	}

	u64 get(int i)
	{
		assert(0 < i && i < 32);
		assert(valid[i]);
		return regs[i];
	}

	void set(int i, u64 value)
	{
		assert(0 < i && i < 32);
		valid[i] = true;
		debug("setting reg %d <-- %lx", i, value);
		regs[i] = value;
	}

	void set(const string& reg_name, u64 value)
	{
		int i = RegNames::get(reg_name);
		set(i, value);
	}

	u64 get(const string& reg_name) const
	{
		debug("get reg_name=%s reg_num=%d", reg_name.c_str(), RegNames::get(reg_name));
		int i = RegNames::get(reg_name);
		assert_msg(valid[i], "reg_name=%s", reg_name.c_str());
		return regs[i];
	}

	void invalidate(const string& reg_name)
	{
		int i = RegNames::get(reg_name);
		invalidate(i);
	}

	void invalidate(int i)
	{
		assert(0 < i && i < 32);
		valid[i] = false;
		regs[i] = 0;
	}
};
