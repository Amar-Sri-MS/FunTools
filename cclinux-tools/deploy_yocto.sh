#!/bin/bash -e
MYDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

fun_image="fun-image-mips64r6hv-mips64r6.tar.xz"



for i in "$@" ; do
    if [ "$i" = "--developer" ]; then
        fun_image="fun-image-mips64r6hv-developer-mips64r6.tar.xz"
        break
    fi
done


tar Jxf bin/cc-linux-yocto/mips64hv/$fun_image -C $DEPLOY_ROOT

#
# By default, don't start NTP.  System specific deployments may add a custom ntp.conf
#

rm -f $DEPLOY_ROOT/etc/ntp.conf

#
# By default, don't create bondX devices when bonding is loaded
#

echo 'options bonding max_bonds=0' > $DEPLOY_ROOT/etc/modprobe.d/bonding.conf

#
# Allow DHCP to change hostname away from mips64r6
#

sed -i -E "/current_hostname\" = 'localhost' ] \|\|\$/a\\           [ \"\$current_hostname\" = 'mips64r6' ] \|\|" $DEPLOY_ROOT/sbin/dhclient-script

#
# Some tools expect ip to be at /bin/ip, create a link if needed.
#
if [ ! -e $DEPLOY_ROOT/bin/ip ] ; then
    ln -s ../sbin/ip $DEPLOY_ROOT/bin/ip
fi

# start sshd early
pushd $DEPLOY_ROOT/etc
for f in `find -regex ".*\/[KS]96sshd"`;  do mv $f ${f/%96sshd/20sshd}; done
popd

patch -p0 -d $DEPLOY_ROOT < $MYDIR/patches/rc.patch
patch -p0 -d $DEPLOY_ROOT < $MYDIR/patches/dhclient-script.patch
patch -p0 -d $DEPLOY_ROOT < $MYDIR/patches/nfsroot.patch

# Core file processing
cp bin/scripts/gzip-stdin $DEPLOY_ROOT/usr/bin
chmod 0755 $DEPLOY_ROOT/usr/bin/gzip-stdin
echo 'kernel.core_pattern = |/usr/bin/gzip-stdin /persist/cores/core.%h.%e.%t.%p.gz' >> $DEPLOY_ROOT/etc/sysctl.conf
echo 'CORE_SIZE=unlimited' >> $DEPLOY_ROOT/etc/default/rcS

# Don't start these by default
rm -f $DEPLOY_ROOT/etc/rc5.d/S21avahi-daemon
rm -f $DEPLOY_ROOT/etc/rc5.d/S87redis-server

# Allow VFIO to work
mkdir -p $DEPLOY_ROOT/etc/modprobe.d/
cp bin/mips64/Linux/vfio.conf $DEPLOY_ROOT/etc/modprobe.d/vfio.conf
chmod 0444 $DEPLOY_ROOT/etc/modprobe.d/vfio.conf

# if we are building inside Jenkins, then store some build
# details in the rootfs

if [ ! -z ${JENKINS_URL} -a ! -z ${JOB_NAME} ]; then
    if [ -z ${BLD_NUM} ]; then
        echo "Build running in Jenkins node but BLD_NUM wasn't set. Does this script need fixing?"
        exit 1
    fi
    if [ -z ${DEV_LINE} ]; then
        echo "Build running in Jenkins node but DEV_LINE wasn't set. Does this script need fixing?"
        exit 1
    fi
else
    BLD_NUM="non-Jenkins"
    DEV_LINE="unknown"
fi

echo """devline=${DEV_LINE}
bldnum=${BLD_NUM}""" > $DEPLOY_ROOT/etc/version.build
