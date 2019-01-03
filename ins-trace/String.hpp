class String
{
public:
	static void split_into_2(const string& in, const char split_char,
				 string *o1, string *o2)
	{
		assert(&in != o1);
		assert(&in != o2);
		int pos = in.find(split_char);
		assert(pos != string::npos);
		*o1 = in.substr(0, pos);
		*o2 = in.substr(pos+1);
	}

	static void split_into_3(const string& in, const char *split_chars,
				 string *o1, string *o2, string *o3)
	{
		const char *s = split_chars;
		assert(s[0] && s[1] && s[2] == 0);

		int start;
		int end;

		start = 0;
		end = in.find(s[0], start);
		assert(end != string::npos);
		*o1 = in.substr(start, end-start);

		start = end+1;
		end = in.find(s[1], start);
		assert(end != string::npos);
		*o2 = in.substr(start, end-start);

		start = end+1;
		*o3 = in.substr(start);
	}

	static void split_into_4(const string& in, const char *split_chars,
				 string *o1, string *o2, string *o3, string *o4)
	{
		const char *s = split_chars;
		assert(s[0] && s[1] && s[2] && s[3] == 0);

		int start;
		int end;

		start = 0;
		end = in.find(s[0], start);
		assert(end != string::npos);
		*o1 = in.substr(start, end-start);

		start = end+1;
		end = in.find(s[1], start);
		assert(end != string::npos);
		*o2 = in.substr(start, end-start);

		start = end+1;
		end = in.find(s[2], start);
		assert(end != string::npos);
		*o3 = in.substr(start, end-start);

		start = end+1;
		*o4 = in.substr(start);
	}

	static string to_hex_16(u64 value)
	{
		string str;

		for (int i=60; i >= 0; i -= 4) {
			int tmp = (value >> i) & 0xf;
			if (tmp < 10)
				str += (tmp + '0');
			else
				str += (tmp - 10 + 'a');
		}
		return str;
	}

	static string pad(const string& str, int n)
	{
		assert(str.length() <= n);

		n -= str.length();

		string out = str;
		while (n--)
			out += ' ';
		return out;
	}
};
