#! /bin/bash
# load level self-submitting script
# Runs the following loop:
#   1. Read the first line from the text file with commands (single command per line)
#   2. Run the commands
#   3. Removes the corresponding line from the file
# until the file with commands is not empty
#
# useful when running many single jobs - this allows avoid flooding the cluster queues from thousands of jobs,

lock="ll-self-submit.lock"
data=$(pwd)/$1
test -e $data || ( echo "$data does not exist" && exit 1 )

echo "Start"

# do some sleep

while true; do
 echo "command while step"

# wt_max=10     # maximum waiting time [seconds]
# wt=$RANDOM   # waiting time
# let "wt %= $wt_max" # make wt < max_wt
# echo "sleeping $wt sec..."
# sleep $wt


 while [ -e $lock ]; do
   echo "time while step"
   wt_max=10     # maximum waiting time [seconds]
   wt=$RANDOM   # waiting time
   let "wt %= $wt_max" # make wt < max_wt
   echo "lock exists -> waiting for " $wt "sec"
   sleep $wt
 done

 echo "creating lock"
 touch $lock
 cmd=$(head -1 $data)
 if [ -z "$cmd" ]; then
   echo "end of file"
   rm -f $lock
   echo "End1"
   exit 0
 fi
 scratch=$(mktemp)
 tail -n +2 $data > $scratch
 mv -f $scratch $data || echo "failed before running $cmd"
 echo "head data"
 head $data
 echo "removing lock"
 rm -f $lock
 echo "executing: $cmd"
 eval $cmd
done

rm -f $lock

echo "End"
