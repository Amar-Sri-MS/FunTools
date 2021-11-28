#!/bin/bash

server=$1
ilo=$2
iter=$3
sshcount=0
successcount=0
prev_output=0
SECONDS=0

echo "Power cycling server:" $server
ipmitool -I lanplus -H $ilo -U localadmin -P Precious1* chassis power cycle
sleep 10

while true
do
   currdate=`date +"%b%d-%Y-%H%M%S"`
   echo $currdate
   ping -c 2 $server
   if [ $? == 0 ]
   then
	echo 'Ping passing; trying ssh now'
	sleep 2
	while true
	do
		echo $server
		logfilename="~/pcie_cycler/log_powercycle_"$server"_"$sshcount"_"$currdate
		output=`sshpass -p "Precious1*" ssh localadmin@$server "~/pcie_cycler/pcie_cycler_powercycle.sh $logfilename"`
		ret=$?
   		if [ $ret == 0 ]
		then
			sshcount=$(( $sshcount + 1 ))
			errorcount=`echo "$output" | grep 'ERROR' | wc -l`
			if [ $errorcount == 0 ]
			then
				#spd-say Running
				echo PASS
				successcount=$(( $successcount + 1))
			else
				#spd-say Error Please check
				echo FAIL
				echo "$output"
				exit 1
			fi
			echo `date` success-count $successcount sshcount $sshcount
			duration=$SECONDS
			echo "Total Duration: $(($duration/86400)) days, $(($duration%86400/3600)) hours, $(($duration%3600/60)) mins and $(($duration%60)) secs elapsed."

			if [ $successcount -gt $iter ]
			then
                                duration=$SECONDS
                                echo 'Ran for ' $successcount
				echo "Total Duration: $(($duration/86400)) days, $(($duration%86400/3600)) hours, $(($duration%3600/60)) mins and $(($duration%60)) secs elapsed."
				exit 0
			fi

			sleep 10
			ipmitool -I lanplus -H $ilo -U localadmin -P Precious1* chassis power cycle
			sleep 10
			break
		else
			echo FAIL with ret: $ret
			echo "$output"
			if [ $ret == 255 ]
			then
				echo Likely ssh error.. retrying
				continue
			else
				exit 1
			fi
		fi
	done
   fi
   sleep 1
done
echo exiting ..
