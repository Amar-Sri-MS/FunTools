
class InputBitStream {
	FILE *_file;
	u8 _buffer[64*4096];
	u8 *_current;
	u8 *_end;
	size_t _bits_remaining;
public:
	InputBitStream(const char *path)
	{
		_file = fopen(path, "rb");
		assert(_file);
		_current = _end = _buffer;
		_bits_remaining = 8;
	}

	bool try_read_bits(size_t bit_count, u64 *out)
	{
		assert(0 < bit_count && bit_count <= 64);

		u64 value = 0;

		debug("bit_count=%zu", bit_count);
		while (bit_count) {
			if (_current == _end) {
				if (!read_more())
					return false;
				assert(_current < _end);
				assert(_bits_remaining == 8);
			}

			int consume_bits = min(bit_count, _bits_remaining);
			value <<= consume_bits;
			value |= (u64)(*_current >> (8 - consume_bits));
			debug("  get %d bits %lu value=%lx", consume_bits, (u64)(*_current >> (8 - consume_bits)), value);
			*_current <<= consume_bits;
			bit_count -= consume_bits;
			_bits_remaining -= consume_bits;
			if (_bits_remaining == 0) {
				_bits_remaining = 8;
				_current++;
			}
		}
		debug("value=%lu\n\n", value);
		*out = value;
		return true;
	}

	u64 read_bits(size_t bit_count)
	{
		u64 out;

		if (!try_read_bits(bit_count, &out))
			fatal("trace file is not complete");
		return out;
	}

private:

	bool read_more(void)
	{
		size_t len = fread(_buffer, 1, sizeof(_buffer), _file);
		if (len > 0) {
			_current = _buffer;
			_end = _current + len;
			return true;
		}

		if (feof(_file))
			return false;

		fatal("Read failed");
		return false;
	}
};
