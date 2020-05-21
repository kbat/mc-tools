#! /bin/bash
# Comments out unneded #include directives

if [ ! $# -eq 2 ]; then
    echo "Usage: $(basename $0) make-target /path/to/file.cxx"
    exit 1
fi

target=$1
fname=$2

if [ ! -e "$fname" ]; then
    echo "$fname does not exist"
    exit 2
fi

if [ ! -e Makefile -a ! -e GNU‐makefile -a ! -e makefile ]; then
    echo "Makefile does not exist"
    exit 3
fi

tmp=$(mktemp -u)

echo "Safe to remove in $fname:"
grep ^\#include "$fname" |egrep -v OutputLog.h | grep \.h\" | tac | while read -r line; do
    /bin/cp -f "$fname" "$tmp"
    sed -i -e "0,/$line/{/$line/d;}"  "$fname" # remove only first occurrence - helps removing duplicate #includes
    if make -j$(nproc) $target >& /dev/null; then
	echo $line
    else
	/bin/cp -f $tmp $fname
    fi
done

rm -f "$tmp"
