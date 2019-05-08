#!/bin/bash

#
# This script runs the dequeuer with a fake stdin. For some unknown reason
# the dequeuer tries to read stdin and will terminate when it sees EOF.
#
# In our automated post-processing servers (which run as daemons), stdin
# is redirected from /dev/null which will return EOF on reads. This makes
# the dequeuer useless from daemons unless the following workaround is
# done.
#

ARGS=$*

DUMMY_FILE=$(mktemp)

echo "Creating dummy file for stdin: $DUMMY_FILE"

# Run the dequeuer while we redirect stdin to a tail of the dummy file to it
# (this provides a fake stdin). This is run as a background process to simplify
# monitoring from this script.
tail -f $DUMMY_FILE | java -jar "csdqer.jar" $ARGS &

# Record the PID of the java program
DQR_PID=$!

# Loop until we see that the dequeuer is no longer running. At that point,
# issue anything to the dummy file, which will cause tail to exit because
# of a broken pipe (SIGPIPE).
#
# TODO: exit with the return code of the dequeuer
while true; do
    if ps -p $DQR_PID > /dev/null; then
        sleep 10
    else
        echo "EOF" > $DUMMY_FILE
        exit 0
    fi
done
