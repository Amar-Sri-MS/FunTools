
class OutputBitStream {
	FILE *_file;
	u8 _buf[64*1024];
	int _pos;
	int _bits_used;

public:
	OutputBitStream(const char *path)
	: _pos(0), _bits_used(0)
	{
		memset(_buf, 0, sizeof(_buf));
		_file = fopen(path, "wb");
		assert(_file);
		// Write file format version 1.
		write_bits(4, 0b0001);
	}
	~OutputBitStream()
	{
		assert(_pos == 0);
		assert(_bits_used == 0);
		fclose(_file);
	}

	void write_bits(int bit_count, u64 value)
	{
		assert(0 < bit_count && bit_count <= 64);
		assert(0 <= value && (bit_count == 64 || value < (1ULL << bit_count)));

		while (bit_count) {
			assert(0 <= _bits_used && _bits_used < 8);

			int consume_bits = min(bit_count, 8 - _bits_used);
			int new_bits = (value >> (bit_count - consume_bits));

			_buf[_pos] |= (new_bits << (8 - _bits_used - consume_bits));

			bit_count -= consume_bits;
			value &= ((1ULL << bit_count) - 1);
			_bits_used += consume_bits;
			if (_bits_used == 8) {
				_bits_used = 0;
				_pos += 1;
				if (_pos == sizeof(_buf)) {
					flush();
					assert(_pos == 0);
				}
			}
		}
		assert(bit_count == 0);
		assert(value == 0);
	}

	int stale_bits()
	{
		return _bits_used ? (8 - _bits_used) : 0;
	}

	void flush()
	{
		assert(stale_bits() == 0);
		fwrite(_buf, 1, _pos, _file);
		_pos = 0;
		memset(_buf, 0, sizeof(_buf));
	}
};
