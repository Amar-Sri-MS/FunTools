#!/bin/bash
set -ex

#rsync -v -r -e ssh --exclude 'data/' . server11:/home/tahsin/src/perf
rsync -v -r -e ssh \
	--exclude 'data/jobs/*/funos-f1-palladium' \
	--exclude 'data/jobs/*/*perfmon.txt' \
	. server11:/home-local/tahsin/perf

