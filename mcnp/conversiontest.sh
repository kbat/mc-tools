#!/bin/bash

VERBOSE=""

function help {

        echo "Usage: conversiontest [-v] mctal_file "
        exit 0

}

function performTest () {

        echo "Converting..."

        SUM=0
        ALL=0

        if [[ "$VERBOSE" == "-v" ]]; then
                shift 1
        fi

	mctal2root.py $VERBOSE $@
	OUT=$?
	SUM=$(($SUM+$OUT))
	roottest.py $VERBOSE $@
	OUT=$?
	SUM=$(($SUM+$OUT))

	exit $SUM

}

test $# -eq 0 && help 

while getopts "hv" option; do
    case $option in
        h) help;;
        v) VERBOSE="-v";;
    esac
done

performTest $@

