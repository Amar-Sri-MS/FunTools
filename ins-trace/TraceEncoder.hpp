
class TraceEncoder : public InsReceiver<Ins> {
	OutputBitStream _out;
	u64 _last_cycle;
	u64 _last_pc;

public:
	TraceEncoder(const char *path)
	: _last_cycle(0), _last_pc(0), _out(path)
	{
	}

	void accept(const Ins& ins)
	{
		u64 c = ins.cycle - _last_cycle;
		u64 p = ins.pc - (_last_pc + 4);

		_last_cycle = ins.cycle;
		_last_pc = ins.pc;

		switch (c) {
		case 0:
			_out.write_bits(2, 0b00);
			break;
		case 1:
			_out.write_bits(2, 0b01);
			break;
		case 2:
			_out.write_bits(3, 0b100);
			break;
		case 3:
			_out.write_bits(3, 0b101);
			break;
		default:
			_out.write_bits(2, 0b11);
			assert(c >= 4);

			int bit_count = bits_for_value(c);
			assert(3 <= bit_count && bit_count <= 64);
			_out.write_bits(6, bit_count - 1);
			_out.write_bits(bit_count, c);
			break;
		}

		if (p == 0) {
			_out.write_bits(1, 0b0);
		} else {
			if ((p & (1ULL << 63)) == 0) {
				_out.write_bits(2, 0b10);
			} else {
				_out.write_bits(2, 0b11);
				p = -p;
			}

			int bit_count;

			// Optimize common case.
			if (p % 4 == 0) {
				p /= 4;
				bit_count = bits_for_value(p);
				assert(bit_count <= 62);
			} else {
				bit_count = 64;
			}
			assert(1 <= bit_count && bit_count <= 64);
			_out.write_bits(6, bit_count - 1);
			_out.write_bits(bit_count, p);
		}

		u64 v = ins.reg_value;

		if (ins.reg_num == 0) {
			_out.write_bits(1, 0b0);
		} else {
			if ((v & (1ULL << 63)) == 0) {
				_out.write_bits(2, 0b10);
			} else {
				_out.write_bits(2, 0b11);
				v = ~v;
				assert((v & (1ULL << 63)) == 0);
			}
			_out.write_bits(5, ins.reg_num);
			int bit_count = bits_for_value(v);
			if (bit_count == 0) {
				assert(v == 0);
				bit_count = 1;
			}
			assert(1 <= bit_count && bit_count <= 64);
			_out.write_bits(6, bit_count - 1);
			_out.write_bits(bit_count, v);
		}
	}

	virtual void finish()
	{
		int stale_bits = _out.stale_bits();
		if (stale_bits) {
			// fill remaining bits with 1s
			_out.write_bits(stale_bits, (1ULL << stale_bits) - 1);
			assert(_out.stale_bits() == 0);
		}

		_out.flush();
	}

private:
	int bits_for_value(u64 v)
	{
		if (v != 0)
			return 64 - __builtin_clzl(v);
		else
			return 0;
	}
};
