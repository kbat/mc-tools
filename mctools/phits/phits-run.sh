#!/usr/bin/env bash

usage()
{
    echo "Usage: $(basename $0) file.inp [prefix] [njobs]"
    echo "       file.inp: PHITS input file. Must contain the 'rseed = 0' string in the [Parameters] section"
    echo "       prefix:   temporary folder prefix. Default: 'case'"
    echo "       njobs:    number of jobs to run. Default: number of cores (output of nproc)"
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

if ! grep -Eq "^\s*rseed\s*=\s*0" broomstick.inp; then
    echo "ERROR: The 'rseed = 0' string is not found in $inp"
    usage
fi

for ((i=1; i<=$njobs; i++)); do
    d=$prefix$i
    if [ -d $d ]; then
	echo "ERROR: $d folder already exists"
	exit 2
    else
	mkdir -p $d
	cat $inp | sed "s;rseed *= *0;rseed = $i;" | sed "s; *\$OMP=.*;\$OMP=1;" > $d/phits.inp
    fi
done

if which parallel > /dev/null; then
    echo parallel "cd {} && phits.sh phits.inp" ::: $prefix*
else
    h=$(pwd)
    for d in $prefix*; do
	echo $d
	cd $d
	phits.sh phits.inp &
	cd $h
    done
    wait $(jobs -rp)
fi
