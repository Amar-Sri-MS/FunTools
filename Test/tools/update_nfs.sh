#!/bin/bash
#set -x

TMPLOC="/tmp/download"

#
# Update the following information if needed
#
CONTROLLER="10.1.80.51"
NFSLOC="eruan-ds200-2"
IMAGEVER="latest"
CHIP="s1"
DIR="/tmp/nfs-mount"
VSWITCH=0
usage() {
    echo ""
    echo "Usage :"    
    echo "Update Latest S1 ROOTFS to a given NFS LOC :        ./update_nfs.sh --nfsroot /tmp/nfs-mount --nfs eruan-ds200-2 --controller 10.1.80.51"
    echo "Update Latest S1 ROOTFS to a given NFS LOC with fm_agent:        ./update_nfs.sh --nfsroot /tmp/nfs-mount --nfs eruan-ds200-2 --controller 10.1.80.51 --vswitch"
    echo "Update Latest F1 ROOTFS to a given NFS LOC :        ./update_nfs.sh --nfsroot /tmp/nfs-mount --nfs eruan-fs4-0 --chip f1 --controller 10.1.80.51"
    echo "Update version 13220 F1 ROOTFS to a given NFS LOC : ./update_nfs.sh --nfsroot /tmp/nfs-mount --nfs eruan-fs4-0 --ver 13220 --chip f1 --controller 10.1.80.51"
    echo ""
}

while test $# -gt 0
do
    case "$1" in
	--ver )
            IMAGEVER=$2
	    shift
            ;;
	--chip )
            CHIP=$2
	    shift
            ;;
	--vswitch )
	    VSWITCH=1
	    if [ ! -d "$WORKSPACE/PCIeFabricManager" ]; then
		echo "Need to pull PCIeFabricManager"
		exit 1
	    fi
	    ;;
	--nfs )
            NFSLOC=$2
	    shift
            ;;
	--nfsroot )
            DIR=$2
	    shift
            ;;	
	--controller )
            CONTROLLER=$2
	    shift
            ;;
        *)
            usage
	    exit 1
            ;;
    esac
    shift
done

IMAGENAME="${CHIP}-rootfs.tar.xz"

download_image() {
    mkdir -p $TMPLOC
    cd $TMPLOC
    rm -f $IMAGENAME
    wget http://dochub.fungible.local/doc/jenkins/master/funsdk/$IMAGEVER/Linux/$IMAGENAME -q --show-progress
    wget http://dochub.fungible.local/doc/jenkins/master/funsdk/$IMAGEVER/build_info.txt -q

}

update_nfs_rootfs() {
    cd $DIR/$1
    sudo rm -rf *
    sudo tar xf $TMPLOC/$IMAGENAME -C $DIR/$1
    sudo cp $TMPLOC/build_info.txt $DIR/$1
}

get_fm_agent_codes() {
    echo "Copy fm_agent codes"
    sudo cp -r $WORKSPACE/PCIeFabricManager/fm_agent/ $DIR/$1/opt/fungible/
    sudo chmod a+x $DIR/$1/opt/fungible/fm_agent/fm_agent.py
}

update_ztp() {
    cd $DIR/$1
    sudo mkdir -p persist/config/ztp
    cd persist/config/ztp
    sudo touch startup_cfg.json
    sudo chmod a+rw startup_cfg.json
    echo "{ \"mgmtif\" : \"eth0\", \"controllers\" : \"$CONTROLLER\"}" > startup_cfg.json

}

update_log(){
    cd $DIR/$1
    VER=$(cat ./build_info.txt)
    sudo touch $1.txt
    sudo chmod a+rw $1.txt
    sudo echo "Create ROOFS from ${VER} for $CHIP, $(date) vswitch $VSWITCH"> $1.txt
    echo "Updated $DIR/$1/ from $IMAGENAME  : ${IMAGEVER}"
    ls -l $DIR/$1/$1.txt
    cat $DIR/$1/$1.txt

}

update_nfs() {
    update_nfs_rootfs $1
    if [ $VSWITCH -eq 1 ]; then
	get_fm_agent_codes $1
    fi
    update_ztp $1
    update_log $1
}


download_image
update_nfs $NFSLOC


