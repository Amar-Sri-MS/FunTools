#! /usr/bin/env bash

SSIZE=""

for i in {1..32}
do
    ((DIS_RINGS=(0xFFFFFFFFFFFFFFFF << $i)))
    DIS_RINGS_HEX=`printf '0x%X' "$DIS_RINGS"`
    RINGS="-d $DIS_RINGS_HEX"

    for CLOCK_DIV in {1..40}
    do
	# check for number of jobs waiting < 15
	while [ `wget -O - http://fun-on-demand-01:9004/?format=json | jq .stats.all_jobs.wait_job_count` -gt 15 ]
	do
	    echo "waiting: too many jobs" && sleep 1m
	done

	# check for being allowed to post a new job
	while wget -O - http://fun-on-demand-01:9001/robotstate | jq .robot_stop | grep true
	do
	    echo "waiting for queue " && sleep 1m
	done

	CLOCK=" -c $CLOCK_DIV"
	DESC="trng $RINGS $CLOCK $SSIZE"

	sed "s|<description>|$DESC|g" trng_run.params > trng_run_filled.params
	echo " $RINGS $CLOCK $SSIZE" >> trng_run_filled.params
	./run_f1.py --wait-until-accepted --params ../fod/trng_run_filled.params funos-f1.signed  2>&1
    done
done
