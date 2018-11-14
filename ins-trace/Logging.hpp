
void fatal(const char *fmt, ...);

#define LOG_ERROR 	1
#define LOG_WARN 	2
#define LOG_INFO 	3
#define LOG_DEBUG 	4

#define LOG_LEVEL LOG_INFO

#if LOG_LEVEL >= LOG_ERROR
#define error(fmt, ...) _log("E " fmt, ##__VA_ARGS__)
#else
#define error(fmt, ...)
#endif

#if LOG_LEVEL >= LOG_INFO
#define info(fmt, ...) _log("I " fmt, ##__VA_ARGS__)
#else
#define info(fmt, ...)
#endif

#if LOG_LEVEL >= LOG_DEBUG
#define debug(fmt, ...) _log("D " fmt, ##__VA_ARGS__)
#else
#define debug(fmt, ...)
#endif

#define _log(_fmt, ...) fprintf(stdout, _fmt "\n", ##__VA_ARGS__)

#define fatal(fmt, ...) ({					\
	fprintf(stderr, "FATAL! " fmt "\n", ##__VA_ARGS__);	\
	abort();						\
})
