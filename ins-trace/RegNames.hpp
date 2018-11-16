
class RegNames {
	static const unordered_map<string, int> name_to_num;
	static const string reg_names[];
public:
	static int get(const string& reg_name)
	{
		return name_to_num.find(reg_name)->second;
	}

	static const string& get(int i)
	{
		assert(0 < i && i < 32);
		return reg_names[i];
	}

	static bool is_reg_name(const string& name)
	{
		return name_to_num.find(name) != name_to_num.end();
	}
};
