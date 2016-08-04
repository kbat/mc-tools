#! /bin/bash
#
# Returns 0 if MCNP(X) geometry check of the given input file is successful
# Adds a 'void' card, removes 'mt' cards and replaces any source definition
# by 'sdef'
#
# https://github.com/kbat/mc-tools
#

if [ $# != 1 -a $# != 2 ]; then
    echo "Usage: geocheck inp N"
    echo "       inp - MCNP(X) geometry to check"
    echo "       N   - number of incident particles (default is 100000)."
    exit 2
fi

inp=$1
if [ ! -r $inp ]; then
    echo "Can't open input file '$inp'"
    exit 3
fi

N=1E+5
if [ $# == 2 ]; then
    N=$2
fi

/bin/cp -f $inp /tmp
inp=/tmp/$inp

N=$(printf "%.0f" $N)
echo "nps: " $N

sed -i "s/^nps.*/nps $N/" $inp

# remove trailing blank lines
sed -i -e :a -e '/^\n*$/{$d;N;ba' -e '}' $inp

# insert void if not there
grep -i "^void *$" $inp || echo void >> $inp

sed -i -n '/^sdef/{p;:a;N;/prdmp/!ba;s/.*\n//};p' $inp
sed -i "s/^sdef.*/sdef/" $inp

sed -i "s/^mt/c mt/" $inp
sed -i "s/^RAND/c RAND/" $inp

rm -f /tmp/geocheck.*
mcnpx i=$inp name=/tmp/geocheck. > /dev/null
out=/tmp/geocheck.o

if grep "run terminated when [[:space:]]* $N particle histories were done" $out; then
    echo "geometry check passed"
    exit 0
else
    echo "geometry check failed"
    echo "input file: " $inp
    echo "output file:" $out
    exit 1
fi
