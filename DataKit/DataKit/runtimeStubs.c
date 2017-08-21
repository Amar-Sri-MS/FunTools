//
//  runtimeStubs.c
//  DataKit
//
//  Created by Bertrand Serlet on 7/22/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

#include <sys/stat.h>

int64_t statSizeForFile(const char *cpath) {
	// Curiously, can't find stat() in Swift
	struct stat buf;
	int err = stat(cpath, &buf);
	if (err == 0) return buf.st_size;
	return -1;
}

