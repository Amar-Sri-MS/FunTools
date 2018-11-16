
template <class O>
class InsDecorator: public InsReceiver<Ins>
{
	const DasmFile &_dasm_file;
	InsReceiver<O> &_out;
public:
	InsDecorator(const DasmFile& dasm_file, InsReceiver<O> *out)
	: _dasm_file(dasm_file), _out(*out)
	{
	}

	void accept(const Ins &ins)
	{
		//printf("%ld: %lx\n", ins.cycle, ins.pc);

		O ins_out(ins, _dasm_file.lookup(ins.pc));
		_out.accept(ins_out);
	}
};
