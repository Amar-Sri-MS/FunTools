
class TextReader
{
	FILE *_file;
	char _buffer[4096];

public:
	TextReader(const char *path)
	{
		_file = fopen(path, "rb");
		assert(_file);
	}
	~TextReader()
	{
		fclose(_file);
	}

	bool get_line(string& line)
	{
		if (NULL == fgets(_buffer, sizeof(_buffer), _file)) {
			assert(feof(_file) != 0);
			return false;
		}

		int len = strlen(_buffer);
		assert(len != sizeof(_buffer));
		assert(len != 0);

		if (_buffer[len - 1] == '\n') {
			_buffer[--len] = 0;
		} else {
			assert(feof(_file) != 0);
		}
		line = _buffer;
		return true;
	}

};
