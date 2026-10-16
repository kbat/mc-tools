#! /usr/bin/env bash

if [ $# != 1 ]; then
    echo "Usage: $0 /path/to/folder"
    exit 1
fi

d=$1

if [ ! -d "$d" ]; then
    echo "Usage: can't find folder $d"
    exit 1
fi

files=$(find "$d" -type f -name batch.out)
echo $files

if [ ${#files} -lt 1 ]; then
    echo "No batch.out in the folder $d"
    exit 1
fi

sed -i -e "s;.*<--- number of remaining batches;0 <--- number of remaining batches;;" "$files"
