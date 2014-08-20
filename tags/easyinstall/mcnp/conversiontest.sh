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
	OUT=0

        if [[ "$VERBOSE" == "-v" ]]; then
                shift 1
        fi

	mctal2root.py $VERBOSE $@
	OUTC=$?
	roottest.py $VERBOSE $@
	OUTT=$?

	if [ $OUTC -ge 1 ] || [ $OUTT -ge 1 ]; then
		OUT=1
	fi

	SUM=$(($SUM+$OUT))
	ALL=$(($ALL+1))

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

