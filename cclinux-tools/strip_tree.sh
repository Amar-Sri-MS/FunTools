#!/bin/bash -e
#
# Find and strip all ELF files under $DEPLOY_ROOT
#
function usage() {
    echo "Usage: $0 [root_dir [yocto-env-file]]"
    exit 1
}

if [ $# -lt 1 ] ; then
    if [ -z "$DEPLOY_ROOT" ] ; then
	echo "No root specified and DEPLOY_ROOT not set"
	exit 1
    fi
else
    DEPLOY_ROOT=$1
fi

if [ $# -gt 1 ] ; then
    yocto_env=$2
else
    if [ -z "$YOCTO_TOOLCHAIN_DIR" -o -z "$YOCTO_MIPS_ENV" ] ; then
	echo "YOCTO_TOOLCHAIN_DIR or YOCTO_MIPS_ENV not set"
	exit 1
    fi
    yocto_env="$YOCTO_TOOLCHAIN_DIR/$YOCTO_MIPS_ENV"
fi

#
# We will use Yocto's strip command as that is the toolchain that
# built everything
#
# Yocto doesn't like to set environment if LD_LIBRARY_PATH is set. So,
# save and restore LD_LIBRARY_PATH around 'source' command in case we
# are running under "pseudo"

orig_ld_library_path=$LD_LIBRARY_PATH
orig_ld_preload=$LD_PRELOAD

unset LD_LIBRARY_PATH LD_PRELOAD

source $yocto_env

if [ -n "$orig_ld_library_path" ] ; then
    if [ -n "$LD_LIBRARY_PATH" ] ; then
	export LD_LIBRARY_PATH=$orig_ld_library_path:$LD_LIBRARY_PATH
    else
	export LD_LIBRARY_PATH=$orig_ld_library_path
    fi
fi
if [ -n "$orig_ld_preload" ] ; then
    if [ -n "$LD_PRELOAD" ] ; then
	export LD_PRELOAD="$orig_ld_preload $LD_PRELOAD"
    else
	export LD_PRELOAD=$orig_ld_preload
    fi
fi

find $DEPLOY_ROOT -type f | (
    while read fname ; do
	if file $fname | grep -q ELF ; then
	    case $fname in
		*.ko)
		    #echo "Stripping $fname as module"
		    ${STRIP} --strip-debug $fname
		    ;;
		*)
		    #echo "Stripping $fname"
		    ${STRIP} $fname
		    ;;
	    esac
	fi
    done
)

# Run depmod
kernel_version=$(ls bin/cc-linux-yocto/mips64hv/System.map-* | sed -e 's/.*System.map-//')

find $DEPLOY_ROOT/lib/modules/$kernel_version -name modules.\* | (
    while read fname ; do
	case $fname in
	    *modules.order | *modules.builtin)
		: # Keep it
		;;
	    *)
		rm -f $fname # Remove it.
		;;
	esac
    done
)

depmod -b $DEPLOY_ROOT -C $DEPLOY_ROOT/etc/depmod.d -F bin/cc-linux-yocto/mips64hv/System.map $kernel_version
