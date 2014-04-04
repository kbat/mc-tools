#!/bin/bash

VERBOSE=""

function help {

	echo "Usage: loop_convert [-v] file1 file2 ... "
	exit 0   

}

function performTest () {

	echo "Converting..."

	SUM=0
	ALL=0

	if [[ "$VERBOSE" == "-v" ]]; then
		shift 1
	fi

	for f in $@;
	do
		echo $f
		conversiontest.sh $VERBOSE $f
		OUT=$?
		if [ $OUT -gt 0 ]; then
			echo $f >> backROOT_fails 
			SUM=$(($SUM+$OUT))
		fi
		ALL=$(($ALL+1))
	done

	echo "$SUM out of $ALL Failed"
	exit $SUM

}

if test $# -eq 0; then
    help
fi

while getopts "hv" option; do
    case $option in
        h) help;;
	v) VERBOSE="-v";;
    esac
done

performTest $@

