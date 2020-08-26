#!/bin/bash

socat TCP4-LISTEN:2661,fork,reuseaddr EXEC:"./funtail-server /tmp/logs --namedpath=/tmp/named"
