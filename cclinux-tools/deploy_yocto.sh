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
