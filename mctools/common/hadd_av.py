#! /usr/bin/python2 -W all

from __future__ import print_function
from sys import argv, exit
from string import ascii_lowercase, digits
from os  import system
from random import choice

def main():
    """
    hadd + average
    """

    outfile = argv[1]
    tmpfname = '/tmp/hadd-av' + ''.join(choice(ascii_lowercase + digits) for x in range(8)) + '.root'
    print(tmpfname)

 #   open(tmpfile).close()
    files = argv[2:]
    nfiles = len(files)

    if system("hadd %s %s" % (tmpfname, ' '.join(files))): exit(1)

    print('number of files:', nfiles)

if __name__ == '__main__':
    exit(main())
