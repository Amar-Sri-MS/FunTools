
enum OpClass {
	Regular,
	BranchCompact,
	BranchDelay,
};

class OpType
{
	static unordered_map<string, OpClass> op_map;

public:
	static bool is_branch(const string& op, bool *has_delay_slot)
	{
		auto it = op_map.find(op);
		if (it != op_map.end()) {
			*has_delay_slot = (it->second == BranchDelay);
			return it->second != Regular;
		}
		assert_msg(0, "%s", op.c_str());
		return false;
	}

};
