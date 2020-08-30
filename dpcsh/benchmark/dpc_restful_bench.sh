#!/bin/bash
set -B                  # enable brace expansion
curl --insecure 'https://localhost:5000/'
echo
for i in {1..300}; do
  curl --silent --insecure --output /dev/null 'https://localhost:5000/'
done
