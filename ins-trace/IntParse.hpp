
class IntParse
{
public:
	static u64 hex_fixed(const char *str, int len)
	{
		u64 value = 0;

		for (int i=0; i < len; i++) {
			value <<= 4;
			if (str[i] > '9') {
				assert_msg('a' <= str[i] && str[i] <= 'f', "%s", str);
				value += str[i] - 'a' + 10;
			} else {
				assert_msg('0' <= str[i] && str[i] <= '9', "%s i=%d", str, i);
				value += str[i] - '0';
			}
		}
		return value;
	}

	static u64 hex_till(const char *str, char stop_char)
	{
		const char* end = strchr(str, stop_char);
		assert(end != NULL);
		return hex_fixed(str, end-str);
	}

	static u64 hex_fixed(const string& str, int len)
	{
		return hex_fixed(str.c_str(), len);
	}

	static u64 hex_16(const string& str)
	{
		assert(str.length() == 16 || (str.length() > 16 && isspace(str[16])));
		return hex_fixed(str.c_str(), 16);
	}

	static u64 hex(const string& str)
	{
		return hex_till(str.c_str(), '\0');
	}

	static u64 decimal_till(const char *str, char stop_char)
	{
		u64 value = 0;

		assert(*str != stop_char);
		do {
			value *= 10;
			assert_msg('0' <= *str && *str <= '9', "str=%s", str);
			value += *str - '0';
		} while (*(++str) != stop_char);
		return value;
	}

	static u64 decimal(const string& str)
	{
		return decimal_till(str.c_str(), '\0');
	}

	static s64 signed_decimal(const string& str)
	{
		if (str[0] == '-')
			return -decimal_till(str.c_str()+1, '\0');
		else
			return decimal_till(str.c_str(), '\0');
	}
};
