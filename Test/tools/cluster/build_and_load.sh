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

update_sdk() {
	sdkup_cmd="./scripts/bob"
	kernel_cmd="./scripts/bob"
	if [ ! -z "$1" ];
	then
		rel_branch=$1
		sdkup_cmd="${sdkup_cmd} -R ${rel_branch}"
		kernel_cmd="${kernel_cmd} -R ${rel_branch}"
	fi

	if [ ! -z "$2" ];
	then
		bld_num=$2
		sdkup_cmd="${sdkup_cmd} -v ${bld_num}"
		kernel_cmd="${kernel_cmd} -v ${bld_num}"
	fi

	sdkup_cmd="${sdkup_cmd} --sdkup"
	kernel_cmd="${kernel_cmd} -H Linux --sdkup cc-linux-yocto.mips64"
	echo $sdkup_cmd
	echo $kernel_cmd
	cd $WORKSPACE/FunSDK/
	./scripts/bob --clean-all --sure
	eval "$sdkup_cmd"
	eval "$kernel_cmd"
}

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

	release=$2
	cd $WORKSPACE/FunOS/
	if [ -f "fv.file.list.yocto" ]; then
		make -j4 MACHINE=$1 NDEBUG=$release SIGN=1 LTO=1 XDATA_LISTS=fv.file.list.yocto
	else
		echo $WORKSPACE/FunSDK/bin/cc-linux-yocto/mips64hv/vmlinux.bin > fv.file.list.yocto
		make -j4 MACHINE=$1 NDEBUG=$release SIGN=1 LTO=1 XDATA_LISTS=fv.file.list.yocto
	fi
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
		scp build/"$USER"-funos-s1.signed.gz "$USER"@vnc-shared-05:/home/"$USER"/tftpboot
	else
		gzip build/funos-f1.signed
		mv build/funos-f1.signed.gz build/"$USER"-funos-f1.signed.gz
		scp build/"$USER"-funos-f1.signed.gz "$USER"@vnc-shared-05:/home/"$USER"/tftpboot
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
		cd $WORKSPACE/Integration/tools/platform/utils/myFabCmds
		fab -f flib.py setup:$2 bridgeS tftpS
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

attach_volumes_help() {
	echo -e "--attach-volumes <setup_name> <numvols> <voltype> <encrypt> <compress> <rds/net> <host_name>"
	echo -e "	setup_name: Name of the system setup"
	echo -e "	numvols:    Number of volumes to be attached"
	echo -e "	voltype:    Type of volume to be attached: durable/raw"
	echo -e "	encrypt:    Whether encryption is enabled"
	echo -e "	compress:   Whether compression is enabled"
	echo -e "	rds/net:    Attach mechanism...rds for FC cards...net for TCP attach"
	echo -e "	host_name:  Name of the host server where volumes are to be attached"
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
	via=$6
	host=$7
	for i in $(seq 1 $numvols);
	do
		volname="$voltype-vol-$i"
		fab -f flib.py cluster_setup:"$setup" attach_vol_to_host:vol_name="$volname",host_name="$host",via=$via,rno=$i,cno=1,nsid=$i,encrypt=$4,compress=$5
	done
}

detach_volumes_help() {
	echo -e "--detach-volumes <setup_name> <numvols> <voltype> <host_name> <rds/net>"
	echo -e "	setup_name: Name of the system setup"
	echo -e "	numvols:    Number of volumes to be detached"
	echo -e "	voltype:    Type of volume to be detached: durable/raw"
	echo -e "	host_name:  Name of the host server where volumes are to be detached"
	echo -e "	rds/net:    Detach mechanism...rds for FC cards...net for TCP detach"
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
	host_name=$4
	via=$5
	for i in $(seq 1 $numvols);
	do
		volname="$voltype-vol-$i"
		fab -f flib.py cluster_setup:"$setup" detach_vol_to_host:vol_name="$volname",host_name="$host_name",via=$via,rno=$i,cno=1,nsid=$i
	done

	if [ $via == "rds" ]
	then
		fab -f flib.py cluster_setup:"$setup" rds_delete_controller:cno=1
	fi
}

delete_volumes() {
	if [ ! -d $WORKSPACE/Integration ]
	then
		echo "Integration directory does not exist"
		exit -1
	fi
	cd $WORKSPACE/Integration/tools/platform/utils/myFabCmds

	setup=$1
	prefix=$2
	fab -f flib.py cluster_setup:"$setup" delete_volumes_with_prefix:prefix="$prefix"
}

lsv_benchmark() {
	if [ ! -d $WORKSPACE/Integration ]
	then
		echo "Integration directory does not exist"
		exit -1
	fi
	cd $WORKSPACE/Integration/tools/platform/utils/myFabCmds

	setup=$1

	for queue in {2..16}
	do
		for qdepth in {4..16}
		do
			for idx in {0..11}
			do
				cmd_str='storage { "class": "controller"\, "opcode": "MODIFY_QOS_TABLE"\, "params": { "type": "lsv"\, "iops": 800000\, "num_queues": '
				cmd_str+=$queue
				cmd_str+='\, "rds_qdepth": '
				cmd_str+=$qdepth
				cmd_str+='\, "tcp_qdepth": '
				cmd_str+=$qdepth
				cmd_str+='\, "idx": '
				cmd_str+=$idx
				cmd_str+=' } }'
				fab -f flib.py cluster_setup:$setup dpcshF:index=0,cmd="$cmd_str"
				fab -f flib.py cluster_setup:$setup dpcshF:index=1,cmd="$cmd_str"
			done
			fab -f flib.py cluster_setup:"$setup" dpcshF:index=0,cmd='peek storage/ctrlr/qos/lsv'
			fab -f flib.py cluster_setup:"$setup" dpcshF:index=1,cmd='peek storage/ctrlr/qos/lsv'
			create_ec_volumes "$setup" 1 256G True True
			attach_volumes "$setup" 1 durable True True net cab08-perf-01
			echo "perform fio with $queue queues and $qdepth qdepth"
			fab -f flib.py cluster_setup:"$setup" host_perfio:nvols=1
			detach_volumes "$setup" 1 durable cab08-perf-01 net
			delete_volumes "$setup" "durable"
		done
	done
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
	echo -e "--update-sdk <rel_branch> <bld_num> Updates FunSDK"
	echo -e "--compile s1/f1 <release> Build s1/f1 FunOS image"
	echo -e "--clean                   Clean up FunOS image"
	echo -e "--upload s1/f1            Upload FunOS image to tftp server"
	echo -e "--run s1/f1 <setup_name>  Run the FunOS image on s1/f1 setup"
	echo -e "--format-drives <setup_name> Formats all drives in the setup"
	echo -e "--create-raw <setup_name> <numvols> <volsize> <encrypt> Creates raw volumes"
	echo -e "--create-ec <setup_name> <numvols> <volsize> <encrypt> <compress> Creates ec volumes"
	echo -e "--attach-volumes <setup_name> <numvols> <voltype> <encrypt> <compress> <rds/net> <host_name> Attach volumes of type voltype to host"
	echo -e "--detach-volumes <setup_name> <numvols> <voltype> <host_name> <rds/net> Detach volumes of type voltype from host"
	echo -e "--delete-volumes <setup_name> <prefix> Deletes volumes with prefix"
	echo -e "--lsv-benchmark <setup_name> Runs lsv benchmark on setup"
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
		--update-sdk)
		fetch_workspace
		shift # past argument
		update_sdk $1 $2
		shift # past value
		shift # past second value
		;;
		--compile)
		fetch_workspace
		shift # past argument
		compile $1 $2
		shift # past value
		shift # past second value
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
		if [ "$#" -ne 7 ]; then
			attach_volumes_help
			exit 1
		fi
		attach_volumes $1 $2 $3 $4 $5 $6 $7
		shift # past value
		shift # past second value
		shift # past third value
		shift # past forth value
		shift # past fifth value
		shift # past sixth value
		shift # past seventh value
		;;
		--detach-volumes)
		fetch_workspace
		shift # past argument
		if [ "$#" -ne 5 ]; then
			detach_volumes_help
			exit 1
		fi
		detach_volumes $1 $2 $3 $4 $5
		shift # past value
		shift # past second value
		shift # past third value
		shift # past forth value
		shift # past fifth value
		;;
		--delete-volumes)
		fetch_workspace
		shift # past argument
		delete_volumes $1 $2
		shift # past value
		shift # past second value
		;;
		--lsv-benchmark)
		fetch_workspace
		shift # past argument
		lsv_benchmark $1
		shift # past value
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
