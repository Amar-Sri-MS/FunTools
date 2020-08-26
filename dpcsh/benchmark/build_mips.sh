#!/bin/sh
set -e
docker build builder -t gccgo-cross
docker build . -t gccgo-benchmark
docker run --rm gccgo-benchmark cat src > benchmark-mips64r6
chmod a+x benchmark-mips64r6