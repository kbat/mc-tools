#! /bin/bash
#
# Returns 0 if MCNP(X) geometry check of the given input file is successful
# Adds a 'void' card, removes 'mt' cards and replaces any source definition
# by 'sdef'
#
# https://github.com/kbat/mc-tools
#

x=0
y=0
z=0
if [ $# != 1 -a $# != 4 ]; then
    echo "Usage: geocheck inp x y z"
    echo "       inp - MCNP(X) geometry to check"
    echo "       x y z - sdef coordinates"
    exit 2
fi

inp=$1
if [ ! -r $inp ]; then
    echo "Can't open input file '$inp'"
    exit 3
fi

N=1E+7
if [ $# == 4 ]; then
    x=$2
    y=$3
    z=$4
fi

/bin/cp -f $inp /tmp
inp=/tmp/$(basename $inp)

N=$(printf "%.0f" $N)
#echo "nps: " $N

sed -i "s/^nps.*/nps $N/" $inp

# remove trailing blank lines
sed -i -e :a -e '/^\n*$/{$d;N;ba' -e '}' $inp

# insert void if not there
grep -i "^void *$" $inp || echo void >> $inp

sed -i -n '/^[sS][dD][eE][fF]/{p;:a;N;/c ++++/!ba;s/.*\n//};p' $inp
sed -i "s/^sdef.*/sdef x=$x y=$y z=$z/i" $inp

sed -i "s/^mt/c mt/i" $inp
sed -i "s/^rand/c rand/i" $inp

# comment out reflection cards
sed -i "s/^REFLE/c REFLE/" $inp
sed -i "s/^REFF/c REFF/" $inp

rm -f /tmp/geocheck.*
mcnpx i=$inp name=/tmp/geocheck. > /dev/null
out=/tmp/geocheck.o

# if grep "run terminated when [[:space:]]* $N particle histories were done"  $out; then
if grep "particle histories were done" > /dev/null $out; then
    echo "geometry check passed with nps=$N"
    exit 0
else
    tail $out
    echo "geometry check failed"
    echo "input file: " $inp
    echo "output file:" $out
    exit 1
fi
