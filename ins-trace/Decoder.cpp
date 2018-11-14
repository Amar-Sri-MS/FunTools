#include "Headers.hpp"

Decoder::Decoder(const char *path, InsReceiver<Ins> *out)
	: _in(path), _out(out)
{
}

void Decoder::run()
{
	u64 version;

	if (!_in.try_read_bits(4, &version))
		fatal("Could not read file format version");

	if (version != 1)
		fatal("File format version not supported");

	Ins ins;

	// Swallow first instruction if pc is 0.
	if (get_next(&ins) && ins.pc != 0)
		_out->accept(ins);

	while (get_next(&ins))
		_out->accept(ins);

	_out->finish();
}

bool Decoder::get_next(Ins *ins)
{
	u64 tmp_value;
	u64 bit_count;

	// Read cycle field.
	u64 c_kind;
	u64 c;

	if (!_in.try_read_bits(2, &c_kind))
		return false;

	switch (c_kind) {
		case 0b00:
			c = 0;
			break;

		case 0b01:
			c = 1;
			break;

		case 0b10:
			c_kind <<= 1;
			c_kind |= _in.read_bits(1);
			if (c_kind == 0b100)
				c = 2;
			else {
				assert(c_kind == 0b101);
				c = 3;
			}
			break;

		case 0b11:
			if (!_in.try_read_bits(6, &bit_count))
				return false;
			bit_count += 1;
			assert(3 <= bit_count && bit_count <= 64);
			if (!_in.try_read_bits(bit_count, &c))
				return false;
			assert(c >= 4);
			break;

		default:
			assert(0);
			fatal("bad type");
			break;
	}

	// Read pc field.
	u64 p_kind;
	u64 p;

	p_kind = _in.read_bits(1);

	if (p_kind == 0b0) {
		p = 0;
	} else {
		p_kind <<= 1;
		p_kind |= _in.read_bits(1);

		bit_count = _in.read_bits(6);
		bit_count += 1;
		assert(1 <= bit_count && bit_count != 63 && bit_count <= 64);

		tmp_value = _in.read_bits(bit_count);
		if (bit_count <= 62)
			tmp_value *= 4;

		if (p_kind == 0b10) {
			p = tmp_value;
		} else {
			assert(p_kind == 0b11);
			p = -tmp_value;
		}
	}

	// Read register update field.
	u64 v_kind;
	s64 v;
	u64 reg_num;
	u64 reg_value;

	v_kind = _in.read_bits(1);

	if (v_kind == 0b0) {
		reg_num = 0;
		reg_value = 0;
	} else {
		v_kind <<= 1;
		v_kind |= _in.read_bits(1);

		reg_num = _in.read_bits(5);
		bit_count = _in.read_bits(6);
		bit_count += 1;
		assert(1 <= bit_count && bit_count <= 64);

		tmp_value = _in.read_bits(bit_count);
		if (v_kind == 0b10)
			reg_value = tmp_value;
		else {
			assert(v_kind == 0b11);
			debug("tmp_value=%lx", tmp_value);
			reg_value = ~tmp_value;
		}
	}

	cycle += c;
	pc += 4 + p;

	ins->cycle = cycle;
	ins->pc = pc;
	ins->reg_num = reg_num;
	ins->reg_value = reg_value;

	return true;
}
