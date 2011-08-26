#! /bin/bash
#
# Comments / uncomments the epsout line in a PHITS input file

usage()
{
        echo "Usage: epsout (on|off) file.phits"
        echo        off - comment epsout lines
        echo        on - uncomment epsout lines
}

flag=$1
in=$2

if [ $flag == "off" ]; then
        echo "Commenting epsout"
        perl -pi -e "s/^ *epsout/c epsout/" $in
elif [ $flag = "on" ]; then
        echo "Uncommenting epsout"
        perl -pi -e "s/c epsout/  epsout/" $in
else
        echo "asdf"
        usage
        exit 1
fi

