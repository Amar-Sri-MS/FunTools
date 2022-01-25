#!/bin/bash

#
# Script that runs a container for cache miss processing.
#
# The uid of processes running in the container will be the same as the
# user running this script (instead of the default root).
#
# The user must have sudo permissions to run this script.
#

function usage() {
    echo "usage: process_cm.sh job_dir"
    echo "   job_dir    directory containing cache miss data on the host"
    exit 1
}

# Check the argument count
[[ $# -eq 1 ]] || usage

GID=$(id -g)
echo "Running process_cm with uid $UID and gid $GID"

#
# We use bind mounts to mount the specified job directory as the /data/run
# directory in the container. 
#
# Running as the uid of the current user means output files of the
# post-processing step will belong to that uid, and not root.
#
docker run \
  --mount type=bind,source=$1,target=/data/run \
  --user=$UID:$GID \
  docker.fungible.com/cm_local_processing \
  /app/process_perf_f1.py /data/run --custom-infra --parse-mode=cache_miss --skip-missmap
