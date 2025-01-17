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
# Note that we use a FIFO instead of a regular file: this works better
# across different Linux distros when we issue writes to cause a SIGPIPE
# that terminates the tail process.
#
ARGS=$*
DUMMY_DIR=$(mktemp -d)
DUMMY_FILE=$DUMMY_DIR/dqr_fake_fifo
mkfifo $DUMMY_FILE

JAR_DIR=$(dirname $0)

echo "Creating dummy file for stdin: $DUMMY_FILE"

# Run the dequeuer while we redirect stdin to a tail of the dummy file to it
# (this provides a fake stdin). This is run as a background process to simplify
# monitoring from this script.
tail -f $DUMMY_FILE | java -jar "$JAR_DIR/csdqer.jar" $ARGS &

# Record the PID of the java program
DQR_PID=$!
echo "Waiting for DQR $DQR_PID"

# Loop until we see that the dequeuer is no longer running. At that point,
# issue anything to the dummy file, which will cause tail to exit because
# of a broken pipe (SIGPIPE).
while true; do
    if ps -p $DQR_PID > /dev/null; then
        sleep 5
    else
        echo "EOF" > $DUMMY_FILE
        rm -rf $DUMMY_DIR

        # The PID return code will be reserved within the shell until
        # this is called, so there is no danger of PID reuse causing
        # a wait on the wrong subprocess.
        wait $DQR_PID
        exit $?
    fi
done
