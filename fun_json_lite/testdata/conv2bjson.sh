#!/usr/bin/env bash

cd $(dirname $0)
for f in $(ls *.json); do
	fn=$(echo $f | cut -d. -f1)
	ext=$(echo $f | cut -d. -f2)
	out=${fn}.b${ext}
	echo jsonutil -i $f -O $out
	./jsonutil -i $f -O $out
done
