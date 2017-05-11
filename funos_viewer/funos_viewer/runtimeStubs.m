//
//  runtimeStubs.m
//
//  Created by Bertrand Serlet on 4/23/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

#include <Foundation/Foundation.h>
#include <sys/stat.h>

double euclidianSquares(int N, const double *p1, const double *p2) {
    // for comparing C and Swift speed
    int i;
    double sum = 0.0;
    for (i = 0; i < N; i++) {
        double d = p1[i] - p2[i];
        sum += d * d;
    }
    return sum;
}

int64_t statSizeForFile(const char *cpath) {
    // Curiously, can't find stat() in Swift
    struct stat buf;
    int err = stat(cpath, &buf);
    if (err == 0) return buf.st_size;
    return -1;
}
