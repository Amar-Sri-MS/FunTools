# Prepare binaries for CC TFTP from Dochub

We need to prepare two parts of binaries for TFTP.
1. FunOS image with vmlinux image included.
2. Prepare NFS location from achieved rootfs

## Prepare FunOS image

prepare_funos_image_from_dochub.sh could be used to pull a given version's funos image from dochub, add vmlinux image and put the output image at $WORKSPACE. This script requires mips tools chain.

Hints: This script could be used inside FunCP's docker if you don't have mips toolchain installed.
```
localadmin@eruan-vm1:~/workspace/FunControlPlane$ ./scripts/docker/launch_system.py --run
```

### Usage
```

Usage :
Prepare from latest :          ./prepare_funos_image_from_dochub.sh
Prepare from a given version : ./prepare_funos_image_from_dochub.sh --ver 13225


```

### Example
```
localadmin@e6bcf07b742d:~/fungible/FunTools/Test/tools$ ./prepare_funos_image_from_dochub.sh 
funos.mips64-extra. 100%[===================>] 236.75M   426MB/s    in 0.6s    
Adding blob vmlinux.bin from file /home/localadmin/fungible/FunSDK/bin/cc-linux-yocto/mips64hv/vmlinux.bin
<<<<<<< NO 'FUN_HSM_TOKEN' IN ENVIRONMENT ==> DEVELOPMENT BUILD >>>>>>>
signed


-rw-r--r-- 1 localadmin localadmin 79 Dec 12 00:25 /home/localadmin/fungible/funos_image_latest.txt
-rw-r--r-- 1 localadmin localadmin 10138729 Dec 12 00:25 /home/localadmin/fungible/funos-s1-release.signed.gz

funos-s1-release.signed.gz from version latest at Sat Dec 12 00:25:33 PST 2020
```

## Prepare NFS
### Usage
```
Usage :
Update Latest S1 ROOTFS to a given NFS LOC for vswtich:        ./update_nfs.sh --nfsroot /tmp/nfs-mount --nfs eruan-ds200-2 --controller 10.1.80.51 --vswitch
Update Latest S1 ROOTFS to a given NFS LOC :        ./update_nfs.sh --nfsroot /tmp/nfs-mount --nfs eruan-ds200-2 --controller 10.1.80.51
Update Latest F1 ROOTFS to a given NFS LOC :        ./update_nfs.sh --nfsroot /tmp/nfs-mount --nfs eruan-fs4-0 --chip f1 --controller 10.1.80.51
Update version 13220 F1 ROOTFS to a given NFS LOC : ./update_nfs.sh --nfsroot /tmp/nfs-mount --nfs eruan-fs4-0 --ver 13220 --chip f1 --controller 10.1.80.51

```

### Example
```
localadmin@eruan-vm1:~/workspace/FunTools/Test/tools$ ./update_nfs.sh --nfsroot /tmp/nfs-mount --nfs eruan-ds200-2 --controller 10.1.80.51
s1-rootfs.tar.xz               100%[====================================================>]  61.09M  --.-KB/s    in 0.1s    
Updated /tmp/nfs-mount/eruan-ds200-2/ from s1-rootfs.tar.xz  : latest
-rw-rw-rw- 1 root root 62 Dec 12  2020 /tmp/nfs-mount/eruan-ds200-2/eruan-ds200-2.txt
Create ROOFS from latest for s1, Sat Dec 12 00:32:12 PST 2020
```