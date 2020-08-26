#!/bin/bash
set -B                  # enable brace expansion
curl 'http://localhost:5000/'
echo
for i in {1..300}; do
  curl --silent --output /dev/null 'http://localhost:5000/'
done
