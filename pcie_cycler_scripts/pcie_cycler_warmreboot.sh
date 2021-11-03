#!/bin/bash

# Print the username and all arguments.
echo "BEFORE Running as: $(id -un)"
echo "Arguments:"
for arg; do echo "  $((++i)): [$arg]"; done

if [ "$UID" != 0 ] 
then
    exec sudo /bin/bash -c "$(command printf '%q ' "$BASH_SOURCE" "$@")"
    exit 0
fi

# Print the username and all arguments.
echo "AFTER Running as: $(id -un)"
echo "Arguments:"
for arg; do echo "  $((++i)): [$arg]"; done


LOG=$1
echo 'Logfile is: ' $LOG

touch $LOG
echo ' ' >> $LOG

date_cur=`date`
echo $date_cur >> $LOG

if lspci | egrep -i 'fungible|1dad' ; then

	ret=$(sudo lspci -d 1dad: -vvv | grep "LnkSta:" | grep -v "Speed 8GT" | wc -l)
	echo $ret >> $LOG

	if [ $ret -eq 0 ]
	then
		echo 'Gen3 link' >> $LOG

		ret=$(sudo lspci -d 1dad: -vvv | grep "LnkSta:" | grep -v "Width x16" | wc -l)
		echo $ret >> $LOG
		if [ $ret -ne 0 ]
		then
			echo 'ERROR: Non x16 link'
			echo 'ERROR: Non x16 link' >> $LOG
			sudo lspci -d 1dad: -vvv  >> $LOG
			sync
			exit 1
		fi

		echo 'x16 link' >> $LOG
		sudo lspci -d 1dad: -vvv  >> $LOG
		sync

		echo "sudo reboot" | at now +1 minutes
		exit 0
	else
		echo 'ERROR: NON Gen3 link!!!!'
		echo 'ERROR: NON Gen3 link!!!!' >> $LOG
		sudo lspci -d 1dad: -vvv  >> $LOG
		sync
		exit 1
	fi
else
	echo 'ERROR: No S1 device !!'
	echo 'ERROR: No S1 device !!' >> $LOG
	sync
	exit 1
fi
