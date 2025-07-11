#!/usr/bin/env bash

function usage()
{
    echo -e """
Prints the material comment string, assuming that the material description line precedes its definition
and contains the word 'Material' - as is the case in CombLayer-generated input files.
"""

    echo "Usage:" $(basename $0) m file.inp
    echo "       m        - material name"
    echo "       file.inp - FLUKA input file"
};


if [ $# != 2 ]; then
    usage
    exit 1
fi

if [ ! -e $2 ]; then
    echo "Can't open file $2"
    exit 1
fi

grep -i -B 1 $1 $2 | grep Material
