#!/usr/bin/env bash

function show_help()
{
    echo "$0: create an iso image from the specified folder"
    echo "Usage:"
    echo "$0 /path/to/folder /path/to/iso_image_file"
    echo ""
}

if [[ ( $@ == "--help") ||  $@ == "-h" ]] ; then
    show_help
    exit 0
fi

# arguments required
if [  $# != 2 ] ; then
    show_help
    echo "Missing argument(s)"
    exit 1
fi


rm $2
hdiutil makehybrid -iso -joliet -o $2 $1
