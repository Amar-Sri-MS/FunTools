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

format_drives() {
	if [ ! -d $WORKSPACE/Integration ]
	then
		echo "Integration directory does not exist"
		exit -1
	fi
	cd $WORKSPACE/Integration/tools/platform/utils/myFabCmds

	setup=$1
	fab -f flib.py cluster_setup:$1 format_drives
}

create_raw_volumes() {
	if [ ! -d $WORKSPACE/Integration ]
	then
		echo "Integration directory does not exist"
		exit -1
	fi
	cd $WORKSPACE/Integration/tools/platform/utils/myFabCmds

	setup=$1
	numvols=$2
	for i in $(seq 1 $numvols);
	do
		fab -f flib.py cluster_setup:"$setup" create_raw_vol:vol_name="raw-vol-${i}",size=$3,encryption=$4
	done
}

create_ec_volumes() {
	if [ ! -d $WORKSPACE/Integration ]
	then
		echo "Integration directory does not exist"
		exit -1
	fi
	cd $WORKSPACE/Integration/tools/platform/utils/myFabCmds

	setup=$1
	numvols=$2
	for i in $(seq 1 $numvols);
	do
		fab -f flib.py cluster_setup:"$setup" create_durable_vol:vol_name="durable-vol-${i}",size=$3,encryption=$4,compress=$5
	done
}

attach_volumes() {
	if [ ! -d $WORKSPACE/Integration ]
	then
		echo "Integration directory does not exist"
		exit -1
	fi
	cd $WORKSPACE/Integration/tools/platform/utils/myFabCmds

	setup=$1
	numvols=$2
	voltype=$3
	for i in $(seq 1 $numvols);
	do
		volname="$voltype-vol-$i"
		fab -f flib.py cluster_setup:"$setup" attach_vol_to_host:vol_name="$volname",host_name="cab08-qa-03",via="rds",rno=$i,cno=1,nsid=$i,encrypt=$4,compress=$5
	done
}

detach_volumes() {
	if [ ! -d $WORKSPACE/Integration ]
	then
		echo "Integration directory does not exist"
		exit -1
	fi
	cd $WORKSPACE/Integration/tools/platform/utils/myFabCmds

	setup=$1
	numvols=$2
	voltype=$3
	for i in $(seq 1 $numvols);
	do
		volname="$voltype-vol-$i"
		fab -f flib.py cluster_setup:"$setup" detach_vol_to_host:vol_name="$volname",host_name="cab08-qa-03",via="rds",rno=$i,cno=1,nsid=$i
	done
	fab -f flib.py cluster_setup:"$setup" rds_delete_controller:cno=1
}

demo_setup() {
	if [ ! -d $WORKSPACE/Integration ]
	then
		echo "Integration directory does not exist"
		exit -1
	fi
	cd $WORKSPACE/Integration/tools/platform/utils/myFabCmds

	dpc_cmd="storage { \"class\": \"controller\", \"opcode\": \"CREATE\", \"params\": { \"ctrlr_id\": 1, \"ctrlr_type\": \"BLOCK\", \"ctrlr_uuid\": \"rem-ctrlrc0000p0\", \"subsys_nqn\":\"nqn.2015-09.com.fungible:c8:2c:2b:00:4d:d8\", \"host_nqn\":\"nqn.2015-09.com.fungible:15.127.1.5\", \"port\": 1099, \"qos\": { \"max_read_only_iops\": 800000, \"max_write_iops\": 200000, \"min_read_only_iops\": 800000, \"min_write_iops\": 200000 }, \"remote_ip\": \"15.127.1.5\", \"transport\": \"TCP\" } }"
	fab -f flib.py setupS:FS242 dpcshF:index=0,cmd=$dpc_cmd

	dpc_cmd="storage { \"class\": \"volume\", \"opcode\": \"VOL_ADMIN_OPCODE_CREATE\", \"params\": { \"block_size\": 4096, \"capacity\": 412316860416, \"name\": \"thin-block1\", \"type\": \"VOL_TYPE_BLK_LOCAL_THIN\", \"uuid\": \"blt-c000000v0000\" } }"
	fab -f flib.py setupS:FS242 dpcshF:index=0,cmd=$dpc_cmd

	dpc_cmd="storage { \"class\": \"volume\", \"opcode\": \"VOL_ADMIN_OPCODE_CREATE\", \"params\": { \"block_size\": 512, \"capacity\": 2098688, \"name\": \"nvvol1\", \"type\": \"VOL_TYPE_BLK_NV_MEMORY\", \"uuid\": \"jvol-00000000000\" } }"
	fab -f flib.py setupS:FS242 dpcshF:index=0,cmd=$dpc_cmd

	dpc_cmd="storage { \"class\": \"volume\", \"opcode\": \"VOL_ADMIN_OPCODE_CREATE\", \"params\": { \"block_size\": 4096, \"capacity\": 274877906944, \"group\": 4, \"jvol_uuid\": \"jvol-00000000000\", \"name\": \"lsv1\", \"pvol_id\": [\"blt-c000000v0000\"], \"type\": \"VOL_TYPE_BLK_LSV\", \"uuid\": \"lsv-000000000000\" } }"
	fab -f flib.py setupS:FS242 dpcshF:index=0,cmd=$dpc_cmd

	dpc_cmd="storage { \"class\": \"controller\", \"opcode\": \"ATTACH\", \"params\": { \"ana_state\": \"optimized\", \"ctrlr_uuid\": \"rem-ctrlrc0000p0\", \"enable_connection\": true, \"nsid\": 1, \"vol_uuid\": \"lsv-000000000000\" } }"
	fab -f flib.py setupS:FS242 dpcshF:index=0,cmd=$dpc_cmd

	dpc_cmd="storage { \"class\": \"controller\", \"opcode\": \"IPCFG\", \"params\": {\"ip\": \"15.127.1.5\" } }"
	fab -f flib.py cluster_setup:storage-dev-1 dpcshS:cmd=$dpc_cmd

	dpc_cmd="storage { \"class\": \"controller\", \"opcode\": \"CREATE\", \"params\": {\"ctrlr_uuid\": \"ctrlr-0000000001\", \"transport\": \"PCI\", \"huid\":1, \"ctlid\":0, \"fnid\":3 } }"
	fab -f flib.py cluster_setup:storage-dev-1 dpcshS:cmd=$dpc_cmd

	dpc_cmd="storage { \"class\": \"volume\", \"opcode\": \"VOL_ADMIN_OPCODE_CREATE\", \"params\": {\"capacity\": 214748364800, \"block_size\": 4096, \"type\": \"VOL_TYPE_BLK_RDS\", \"uuid\": \"rds-000000000001\", \"name\": \"rds1\", \"transport\":\"TCP\", \"remote_nsid\":1, \"remote_ip\":\"15.242.1.2\", \"subsys_nqn\":\"nqn.2015-09.com.fungible:c8:2c:2b:00:4d:d8\", \"host_nqn\":\"nqn.2015-09.com.fungible:15.127.1.5\", \"encrypt\": true, \"key\": \"1e0dc872b9e01c670111dacb0633570834dd4f1736ebcafe2498732d6bc96377\", \"xtweak\": \"8e14735a7e9d4693\", \"compress\": true, \"zip_filter\": \"FILTER_TYPE_DEFLATE\", \"zip_effort\": \"ZIP_EFFORT_15Gbps\", \"port\": 1099 } }"
	fab -f flib.py cluster_setup:storage-dev-1 dpcshS:cmd=$dpc_cmd

	dpc_cmd="storage { \"class\": \"controller\", \"opcode\":\"ATTACH\", \"params\": { \"ctrlr_uuid\": \"ctrlr-0000000001\", \"nsid\":1, \"vol_uuid\": \"rds-000000000001\" } }"
	fab -f flib.py cluster_setup:storage-dev-1 dpcshS:cmd=$dpc_cmd
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
	echo -e "--run s1/f1 <setup_name>  Run the FunOS image on s1/f1 setup"
	echo -e "--format-drives <setup_name> Formats all drives in the setup"
	echo -e "--create-raw <setup_name> <numvols> <volsize> <encrypt> Creates raw volumes"
	echo -e "--create-ec <setup_name> <numvols> <volsize> <encrypt> <compress> Creates ec volumes"
	echo -e "--attach-volumes <setup_name> <numvols> <voltype> <encrypt> <compress> Attach volumes of type voltype to host"
	echo -e "--detach-volumes <setup_name> <numvols> <voltype> Detach volumes of type voltype from host"
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
		--format-drives)
		fetch_workspace
		shift # past argument
		format_drives $1
		shift # past value
		;;
		--create-raw)
		fetch_workspace
		shift # past argument
		create_raw_volumes $1 $2 $3 $4
		shift # past value
		shift # past second value
		shift # past third value
		shift # past forth value
		;;
		--create-ec)
		fetch_workspace
		shift # past argument
		create_ec_volumes $1 $2 $3 $4 $5
		shift # past value
		shift # past second value
		shift # past third value
		shift # past forth value
		shift # past fifth value
		;;
		--attach-volumes)
		fetch_workspace
		shift # past argument
		attach_volumes $1 $2 $3 $4 $5
		shift # past value
		shift # past second value
		shift # past third value
		shift # past forth value
		shift # past fifth value
		;;
		--detach-volumes)
		fetch_workspace
		shift # past argument
		detach_volumes $1 $2 $3
		shift # past value
		shift # past second value
		shift # past third value
		;;
		--demo-setup)
		demo_setup
		shift # past argument
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
