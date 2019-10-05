#!/bin/bash -e

LOG_STASH="/var/log"
ACTIVE_LOG_FILE="COMe-boot-up.log"
LOG_FILE=`echo "$LOG_STASH"/"$ACTIVE_LOG_FILE"`
LOG_FILE_PREFIX="FS1600"
MAX_ARCHIVES=10


if [[ -f $LOG_FILE ]]; then
        NUM_ARCHIVES=`ls $LOG_STASH/$LOG_FILE_PREFIX* 2>/dev/null | wc -l`
        if [[ $NUM_ARCHIVES -ge $MAX_ARCHIVES ]]; then
                # Keep Newest; Delete remaining all
                FILE_LIST=`echo "$LOG_STASH"/"$LOG_FILE_PREFIX"*`
                ls $FILE_LIST | sort | uniq -u | /usr/bin/head -n -$MAX_ARCHIVES | /usr/bin/xargs --no-run-if-empty rm
        fi

	DATE=`date +%m-%d-%Y-%H-%M-%S`
	ARCHIVE_LOG_FILE=`echo "$LOG_STASH"/"$LOG_FILE_PREFIX"_"$DATE"_"$ACTIVE_LOG_FILE".tgz`
	/bin/tar zcvf $ARCHIVE_LOG_FILE $LOG_FILE > /dev/null 2>&1
	rm -f $LOG_FILE
fi

