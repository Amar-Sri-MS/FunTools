#!/bin/bash

socat TCP4-LISTEN:6666,fork,reuseaddr EXEC:"./funtail-server /tmp/logs --namedpath=/tmp/named"
