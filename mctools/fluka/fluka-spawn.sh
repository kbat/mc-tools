#!/usr/bin/env bash

INP=$1
NJOBS=$2

if [ $# -ne 2 ]; then
    echo "FLUKA input file spawner"
    echo "      generates clones of the given input file with different random seeds"
    echo ""
    echo "Usage: $(basename $0) INP njobs"
    echo " INP   FLUKA input file"
    echo " jobs  Number of input files with different random seeds to generate"
    echo ""
    echo "Homepage: https://github.com/kbat/mc-tools"
    exit 1
fi

if [ ! -e "$INP" ]; then
    echo "Can't open $INP"
    exit 1
fi

if [ $NJOBS -le 1 ]; then
    echo "NJOBS must be above 2"
    exit 2
fi

for (( j=1; j<=$NJOBS; j++ )); do
    NEWINP=$(basename $INP .inp)-spawn$j.inp
   cat "$INP" | sed "s;^RANDOMI.*;RANDOMIZE        1.0 $j.0;" > $NEWINP
done
