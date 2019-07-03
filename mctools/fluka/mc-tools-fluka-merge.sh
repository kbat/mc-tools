#! /bin/sh
#
# This is an auxiliary script for fluka2root.
# It simplifies calling the FLUKA merge tools
# with GNU parallel
# The script assumes that the argv[1] extension
# is the FLUKA merge tool name

in="$1"
merge="${in##*.}"

cat $in | $FLUTIL/$merge
