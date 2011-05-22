#! /bin/sh
#
# Sets the values of maxcas and maxbch of the PHTIS input file
#
#

if [ $# != 3 ]; then
    echo "Usage: `basename $0` maxcas maxbch phits.in"
    echo "       maxcas and maxbch - integer values"
    echo "       phits.in - name of the PHITS input file"
    exit 1
fi

maxcas=$1
maxbch=$2
file=$3

echo $maxcas $maxbch $file

perl -pi -e "s/maxcas = \d+/maxcas = $maxcas/" $file
perl -pi -e "s/maxbch = \d+/maxbch = $maxbch/" $file

egrep "(maxcas|maxbch)" $file

