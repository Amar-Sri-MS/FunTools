#! /bin/bash -ex

function show_help()
{
    echo "trng_data.sh: get trng data"
    echo "Usage:"
    echo "./trng_data.sh <options>"
    echo "\nOptions:"
    echo "-d <disabled_rings>: Disable the rings. Default=0"
    echo "-c <clock_divider>: Clock divider"
    echo "-s <sample_size>: Data size (in bytes)"
    echo "\nExample:"
    echo "./trng_data.sh -d 0xF -s 1000000 -c 5"
}

if [[ ( $@ == "--help") ||  $@ == "-h" ]] ; then
    show_help
    exit 0
fi

# default values
RINGS=""
CLOCK=""
SSIZE=""
# parse arguments

#OPT POSIX variable
OPTIND=1 # best practice for getopts

while getopts "hd:c:s:" opt; do
    case "$opt" in
	h) show_help
	   exit 0
	   ;;
	d) RINGS=" -d "$OPTARG
	   ;;
	c) CLOCK=" -c "$OPTARG
	   ;;
	s) SSIZE=" -s "$OPTARG
	   ;;
    esac
done

DESC="trng $RINGS $CLOCK $SSIZE"

sed "s|<description>|$DESC|g" trng_run.params > trng_run_filled.params
echo " $RINGS $CLOCK $SSIZE" >> trng_run_filled.params
./run_f1.py --rootfs-image ../fod/rootfs-images/ --params ../fod/trng_run_filled.params funos-f1.signed  2>&1
echo "    Done!"
