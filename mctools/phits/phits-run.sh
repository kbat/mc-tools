#!/usr/bin/env bash

usage()
{
    echo "Usage: $(basename $0) file.inp [prefix] [njobs]"
    echo "       file.inp: PHITS input file. Must contain the 'rseed = RSEED' string in the [Parameters] section"
    echo "       prefix:   temporary folder prefix"
    echo "       njobs:    number of jobs to run. Default=number of cores (output of nproc)"
    exit 1
}


test $# -eq 0 && usage
test $# -gt 3 && usage

inp=$1
if [ ! -e $inp ]; then
    echo "ERROR: Can't open $inp"
    usage
fi

if [ $# -ge 2 ]; then
    prefix=$2
    if [ $# -eq 3 ]; then
	njobs=$3
    else
	njobs=$(nproc)
    fi
else
    prefix="case"
    njobs=$(nproc)
fi

echo $inp $prefix $njobs
