//
//  Use this file to import your target's public headers that you would like to expose to Swift.
//

#include <CommonCrypto/CommonDigest.h> // for SHA-256

#include <stdint.h>

extern int64_t statSizeForFile(const char *);

// WORKAROUND
// Not defining static_assert causes an error
#define static_assert(x,y)

#include <utils/threaded/fun_json.h>

// Returns <=0 on error
extern int dpcclient_open_socket(void);

extern void dpcclient_test(void);

extern NULLABLE CALLER_TO_FREE const char *dpcrun_command_with_subverb(INOUT int *sock, const char *verb, const char *sub_verb);

extern NULLABLE CALLER_TO_FREE const char *dpcrun_command_with_subverb_and_arg(INOUT int *sock, const char *verb, const char *sub_verb, const char *arg);

extern NULLABLE CALLER_TO_FREE const char *dpcrun_command(INOUT int *sock, const char *verb, const char *arguments_array);
