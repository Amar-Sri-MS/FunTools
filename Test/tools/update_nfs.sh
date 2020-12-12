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

usage() {
    echo ""
    echo "Usage :"    
    echo "Update Latest S1 ROOTFS to a given NFS LOC :        ./update_nfs.sh --nfsroot /tmp/nfs-mount --nfs eruan-ds200-2 --controller 10.1.80.51"
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
}

update_nfs_rootfs() {
    cd $DIR/$1
    sudo rm -rf *
    sudo tar xf $TMPLOC/$IMAGENAME -C $DIR/$1
}

update_ztp() {
    cd $DIR/$1
    sudo touch $1.txt
    sudo chmod a+rw $1.txt
    sudo echo "Create ROOFS from ${IMAGEVER} for $CHIP, $(date)"> $1.txt
    sudo mkdir -p persist/config/ztp
    cd persist/config/ztp
    sudo touch startup_cfg.json
    sudo chmod a+rw startup_cfg.json
    echo "{ \"mgmtif\" : \"eth0\", \"controllers\" : \"$CONTROLLER\"}" > startup_cfg.json

    echo "Updated $DIR/$1/ from $IMAGENAME  : ${IMAGEVER}"
    ls -l $DIR/$1/$1.txt
    cat $DIR/$1/$1.txt
}

update_nfs() {
    update_nfs_rootfs $1
    update_ztp $1
}


download_image
update_nfs $NFSLOC


