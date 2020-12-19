#!/bin/bash

# Before running the script, please make sure to set WORKSPACE to the parent
# directory containing FunOS and FunSDK.
#
# export WORKSPACE=<path to parent directory containing FunOS/FunSDK>
#
# Run the following command to build F1 FunOS image:
#
# ./build_and_load.sh --compile f1
#
# Run the following command to upload s1 FunOS image to tftpboot server.
# The FunOS image will be named as <USER-NAME>-funos-<s1/f1>.signed.gz
#
# ./build_and_load.sh upload s1
#
# Run the following command to start storage initiator with the uploaded
# FunOS image. This will output FunOS logs and can be piped to a file
# for debugging.
#
# ./build_and_load.sh run s1 fc200-9
#
# Run the following command to start F1 FunOS image on the FS1600 setup:
#
# ./build_and_load.sh run f1 storage-dev-1
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
	if [ $1 == "s1" ]
	then
		gzip build/funos-s1.signed
		mv build/funos-s1.signed.gz build/"$USER"-funos-s1.signed.gz
		scp build/"$USER"-funos-s1.signed.gz vnc-shared-05:/home/"$USER"/tftpboot
	else
		gzip build/funos-f1.signed
		mv build/funos-f1.signed.gz build/"$USER"-funos-f1.signed.gz
		scp build/"$USER"-funos-f1.signed.gz vnc-shared-05:/home/"$USER"/tftpboot
	fi
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

test() {
	if [ ! -d $WORKSPACE/Integration ]
	then
		echo "Integration directory does not exist"
		exit -1
	fi
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
	echo -e "--upload s1/f1            Upload FunOS image to tftp server"
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
		shift # past argument
		upload $1
		shift # past value
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
