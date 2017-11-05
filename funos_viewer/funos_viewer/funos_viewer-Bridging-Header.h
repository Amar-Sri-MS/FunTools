//
//  Use this file to import your target's public headers that you would like to expose to Swift.
//

#include <CommonCrypto/CommonDigest.h> // for SHA-256

#include "dpcclient.h"
#include <stdint.h>

extern int64_t statSizeForFile(const char *);
