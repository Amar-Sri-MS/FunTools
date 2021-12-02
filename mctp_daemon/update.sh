#!/bin/bash

set_version() {
	local verstr=$(git describe --tags --abbrev=7 --long HEAD)
	local ver=$(echo $verstr | sed -n "s/\([^0-9]*\)[\s|\t]\?\([0-9]*\)\.\([0-9]*\)\.\([0-9]*\).*/\1.\2.\3.\4/p")

	ghash=$(echo $verstr | sed -n "s/[^-]*-\(.*\)/\1/p")
        name=`echo $ver | cut -d. -f1`
        maj=`echo $ver | cut -d. -f2`
        min=`echo $ver | cut -d. -f3`
        sub=`echo $ver | cut -d. -f4`
}

while [ "$#" -gt 0 ]; do
        case "$1" in
        -p | --path) path="$2"
                shift;;

        *) dir $"Unknown option $1"
                ;;
        esac
        shift
done

: ${filename=fw_version.h}
: ${path=./}
: ${build_file=.build_number}

set_version

VN="${name}${maj}.${min}.${sub}${rc}-${ghash}"
git update-index --really-refresh &>/dev/null
[ -z "$(git diff-index --name-only HEAD --)" ] || VN="$VN-dirty"

branch=$(git branch | egrep "^\*" | sed -n "s/\*\s*\(.*\)/\1/p")

if [ ! -z "$comment_filename" ]; then
	[ -f $comment_filename ] && comment=`cat $comment_filename`
fi

[ -z "$comment" ] && comment="NULL"
[ ! -f $build_file ] && build_number="NA" || build_number=`cat $build_file`

cat << EOF > $path/$filename
#ifndef _REPO_HDR_INC_
#define _REPO_HDR_INC_

#include <stdint.h>

#define VERSION_STR		"$VN"
#define VERSION_STR_LEN		${#VN}

#define GIT_BRANCH		"$branch"
#define GIT_BRANCH_LEN		${#branch}

#define BUILD_NUMBER		"$build_number"

#define COMPILE_DATE		"`date +"%b %d %Y %H:%M:%S"`"
#define FW_EPOCH_TIMESTAMP	(`date +"%s"`)

#define FW_COMMENT		$comment
#define FW_COMMENT_LEN		${#comment}

extern const char version_str[];
extern const char branch[];
extern const char compile_date[];
extern const char build_num[];
extern const uint32_t fw_timestamp;

#endif /* _REPO_HDR_INC_ */
EOF
