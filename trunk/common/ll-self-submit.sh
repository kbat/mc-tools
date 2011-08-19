#! /bin/bash
# load level self-submitting script
# reads the first line from the text file with commands (single command per line),
# executes it and removes it from the file

data=$1
cmd=$(head -1 $data)
test -z "$cmd" && exit 0
echo "command line:" "$cmd"
eval $cmd
scratch=$(mktemp -p /tmp)
tail -n +2 $data > $scratch
mv -f $scratch $data
$0 $1
