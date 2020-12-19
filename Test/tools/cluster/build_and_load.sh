#!/bin/bash

# Before running the script, please make sure to set WORKSPACE to the parent
# directory containing FunOS and FunSDK.
# 
# export WORKSPACE=<path to parent directory containing FunOS/FunSDK>
# 
# Run the following command to build FunOS image:
# 
# ./build_and_load.sh compile
# 
# Run the following command to upload FunOS image to tftpboot server. Once
# upload is complete, you will be able to find the FunOS image at
# localadmin@net91-fc-01:/var/lib/tftpboot directory. The FunOS image will be
# named as <USER-NAME>-funos-s1.signed.gz
# 
# ./build_and_load.sh upload
# 
# Run the following command to start storage initiator with the uploaded
# FunOS image. This will output FunOS logs and can be piped to a file
# for debugging.
# 
# ./build_and_load.sh run
# 
# Run the following command to start a simple FIO test run:
# 
# ./build_and_load.sh test 2 True 8589934592
# 
# The above command will create 2 volumes, each with capacity of 8G and
# encryption enabled. The two volumes will then be attached to the host server
# and FIO read traffic will be started.

compile() {
	if [ -z "$1" ]
	then
		echo "Please specify platform type"
		exit -1
	fi

	if [ $1 != "s1" ] && [ $1 != "f1" ]
	then
		echo "Wrong platform type specified"
		exit -1
	fi

	cd $WORKSPACE/FunOS/
	make -j4 MACHINE=$1 NDEBUG=1 SIGN=1 XDATA_LISTS=fv.file.list.yocto
}

clean() {
	cd $WORKSPACE/FunOS/
	make clean
}

upload() {
	cd $WORKSPACE/FunOS/
	gzip build/funos-s1.signed
	mv build/funos-s1.signed.gz build/"$USER"-funos-s1.signed.gz
	scp build/"$USER"-funos-s1.signed.gz vnc-shared-05:/home/"$USER"/tftpboot
}

run() {
	if [ ! -d $WORKSPACE/Integration ]
	then
		echo "Integration directory does not exist"
		exit -1
	fi

	if [ -z "$1" ]
	then
		echo "Please specify platform type"
		exit -1
	fi

	if [ $1 != "s1" ] && [ $1 != "f1" ]
	then
		echo "Wrong platform type specified"
		exit -1
	fi

	if [ -z "$2" ]
	then
		echo "Please specify setup name"
		exit -1
	fi

	if [ $1 == "s1" ]
	then
		cd $WORKSPACE/Integration/tools/platform/utils/fab-pcieproxy
		fab -f cc_pplib.py setupS:$2 bridgeS tftpS
	else
		cd $WORKSPACE/Integration/tools/platform/utils/myFabCmds
		fab -f flib.py cluster_setup:$2 cluster_action connect_cs
	fi
}

cleanup_testbed() {
	numvols=0
	cd $WORKSPACE/py_fabric_27/fs
	fab -f flib.py cluster_setup:msft1 delete_volumes
}

test() {
	cleanup_testbed

	numvols=$1
	encryption=$2
	volsize=$3
	cd $WORKSPACE/py_fabric_27/fs
	for i in $(seq 1 $numvols);
	do
		echo $volsize
		fab -f flib.py cluster_setup:msft1 create_raw_vol:vol_name="raw-vol-${i}",size="$volsize"
		fab -f flib.py cluster_setup:msft1 attach_vol_to_host:vol_name="raw-vol-${i}",host_name="cab9-qa-08",via="rds",rno=$i,cno=1,nsid=$i,encrypt=$encryption
	done
#ssh localadmin@10.91.0.110 -o StrictHostKeyChecking=no << EOF
#	cd /home/localadmin/wangzi
#	echo Fungible/4u | sudo -S ./fio_read_multiple.sh 8 13 $numvols 60
#	exit
#EOF
}

fetch_workspace() {
	if [ -z "$WORKSPACE" ]
	then
		echo "Need to set WORKSPACE environment variable"
		exit -1
	fi
}

help_menu() {
	echo "Usage:"
	echo -e "--compile s1/f1           Build s1/f1 FunOS image"
	echo -e "--clean                   Clean up FunOS image"
	echo -e "--upload                  Upload FunOS image to tftp server"
	echo -e "--run s1/f1 setup_name    Run the FunOS image on s1/f1 setup"
	echo -e "--test <numvols> <encryption> <volsize> Runs a multi-vol test"
}

main() {
	while [[ $# -gt 0 ]]
	do
	key="$1"
	case $key in
		-h|--help)
		help_menu
		shift # past argument
		;;
		--compile)
		fetch_workspace
		shift # past argument
		compile $1
		shift # past value
		;;
		--clean)
		fetch_workspace
		clean
		shift # past argument
		;;
		--upload)
		fetch_workspace
		upload
		shift # past argument
		;;
		--run)
		fetch_workspace
		shift # past argument
		run $1 $2
		shift # past value
		shift # past second value
		;;
		*) # unknown option
		echo "Wrong command" $1
		shift # past argument
		exit -1
		;;
	esac
	done
}

main "$@"
