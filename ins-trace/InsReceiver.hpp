
template<class I>
class InsReceiver
{
public:
	virtual void accept(const I &ins) = 0;
	virtual void finish() {};
};
