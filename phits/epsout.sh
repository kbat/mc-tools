#! /bin/bash
#
# Comments / uncomments the epsout line in a PHITS input file

usage()
{
        echo "Usage: epsout (on|off) file.phits"
        echo "       off -   comment epsout lines"
        echo "        on - uncomment epsout lines"
        exit 1
}

test $# -eq 2 || usage

flag=$1
in=$2

if [ $flag == "off" ]; then
#        echo "Commenting epsout"
        perl -pi -e "s/^ *epsout/c epsout/" $in
elif [ $flag = "on" ]; then
#        echo "Uncommenting epsout"
        perl -pi -e "s/c epsout/  epsout/" $in
else
        usage
fi

