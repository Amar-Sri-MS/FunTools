class Branch
{
public:
	static bool is_taken(const string& op, const string& op_arg,
				    u64 reloc, const RegContext *context,
				    u64 *branch_target)
	{
		if (op == "b" ||
		    op == "balc" ||
		    op == "bc" ||
		    op == "j") {
			assert_msg(reloc == 0 || reloc == 0x20000000,
				   "reloc=%lx", reloc);
			*branch_target = reloc + IntParse::hex_fixed(op_arg, 16);
			return true;
		}

		if (op == "jr" || op == "jrc" ||
		    op == "jalr" || op == "jalrc" ||
		    op == "jr.hb" ) {
			*branch_target = context->get(op_arg);
			return true;
		}

		if (op == "beqz" || op == "beqzc" ||
		    op == "bnez" || op == "bnezc" ||
		    op == "bgez" ||
		    op == "bgtzc" ||
		    op == "bltz" || op == "bltzc" ||
		    op == "blez" || op == "blezc") {
			const string reg = op_arg.substr(0, op_arg.find(','));
			const string branch_addr = op_arg.substr(reg.length()+1);

			*branch_target = IntParse::hex_fixed(branch_addr, 16);
			if (op == "beqz" || op == "beqzc")
				return context->get(reg) == 0;
			if (op == "bnez" || op == "bnezc")
				return context->get(reg) != 0;
			if (op == "bgez")
				return (long)context->get(reg) >= 0;
			if (op == "bgtzc")
				return (long)context->get(reg) > 0;
			if (op == "bltz" || op == "bltzc")
				return (long)context->get(reg) < 0;
			if (op == "blez" || op == "blezc")
				return (long)context->get(reg) <= 0;
			assert_msg(0, "%s", op.c_str());
		}

		if (op == "beq" || op == "beqc" ||
		    op == "bne" || op == "bnec" ||
		    op == "bltc" ||
		    op == "bgec" ||
		    op == "bltuc" ||
		    op == "bgeuc") {
			const string reg1 = op_arg.substr(0, op_arg.find(','));
			const string reg2 = op_arg.substr(reg1.length()+1, op_arg.find(','));
			const string branch_addr = op_arg.substr(reg1.length()+1+reg2.length()+1);

			*branch_target = IntParse::hex_fixed(branch_addr, 16);
			if (op == "beq" || op == "beqc")
				return context->get(reg1) == context->get(reg2);
			if (op == "bne" || op == "bnec")
				return context->get(reg1) != context->get(reg2);
			if (op == "bltc")
				return (long)context->get(reg1) < (long)context->get(reg2);
			if (op == "bgec")
				return (long)context->get(reg1) >= (long)context->get(reg2);
			if (op == "bltuc")
				return context->get(reg1) < context->get(reg2);
			if (op == "bgeuc")
				return context->get(reg1) >= context->get(reg2);
			assert_msg(0, "%s", op.c_str());
		}

		if (op == "eret") {
			// TODO: can this be filled?
			*branch_target = 0;
			return true;
		}
		assert_msg(0, "op=%s op_arg=[%s]", op.c_str(), op_arg.c_str());
	}
};
