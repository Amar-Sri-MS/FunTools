
class PrintSeparator: public InsReceiver<Ins>
{
	InsReceiver<Ins> &_out;
	bool done;
public:
	PrintSeparator(InsReceiver<Ins> *out)
	: _out(*out)
	{
	}

	void accept(const Ins &ins)
	{
		_out.accept(ins);
		//printf("\n");
	}
};
