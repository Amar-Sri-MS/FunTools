
#define STRINGIFY(x) #x
#define XSTRINGIFY(x) STRINGIFY(x)

#define assert_msg(cond, fmt, ...)	({				\
	if (!(cond)) {							\
		fprintf(stderr, "Assertion failed: (%s, \"" fmt "\")"	\
				" at " __FILE__ ":" XSTRINGIFY(__LINE__)\
				"\n",					\
				#cond, ##__VA_ARGS__);			\
		abort();						\
	}								\
})
