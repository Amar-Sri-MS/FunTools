
class Decoder {
	InputBitStream _in;
	InsReceiver<Ins> *_out;

	u64 cycle = 0;
	u64 pc = 0;
public:
	Decoder(const char *path, InsReceiver<Ins> *out);
	void run();

private:
	bool get_next(Ins *ins);
};
