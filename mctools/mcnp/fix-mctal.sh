#! /usr/bin/env bash

mctal=$1

if [ $# != 1 ]; then
    echo "Usage: $(basename $0) /path/to/mctal"
    exit 1
fi

mctal=$1

if [ ! -e $mctal ]; then
    echo "ERROR: can't open $mctal"
    exit 2
fi

sed -i -e "s;0\([0-9]\)-0.0000;0\1 -0.0000;g" $mctal
