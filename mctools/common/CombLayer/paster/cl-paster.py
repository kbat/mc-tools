#! /usr/bin/python -W all
#
# Paster for CombLayer

from sys import exit,stderr
import argparse, re
import os
import pwd
from datetime import datetime
from mctools import checkPaths

class Paster:
    def __init__(self, m, c):
        """Paster Constructor"""
        self.model = m
        self.className = c
        self.cxxDir = os.path.join("Model", "%sBuild" % self.model)
        self.hDir   = os.path.join("Model", "%sBuildInc" % self.model)
        if checkPaths([self.hDir, self.cxxDir], [], False) == 1: # folder name should be different (blame SA :) )
            self.cxxDir = os.path.join("Model", "%s" % self.model) # e.g. args.model = essLinac
            self.hDir   = os.path.join("Model", "%sInc" % self.model)

        self.now = datetime.now()

    def setAuthor(self, val):
        self.author = val

    def setNamespace(self, val):
        self.namespace = val

    def setDescription(self, val):
        self.description = val

    def processSource(self, source):
        dest = os.path.join(self.cxxDir, self.className + ".cxx")
        self.process(source, dest)

    def processHeader(self, header):
        dest = os.path.join(self.hDir, self.className + ".h")
        self.process(header, dest)
    
    def process(self, source, dest):
        """
        Processes file from source to dest
        """

        if os.path.isfile(dest):
            print "File %s exists -> aborting" % dest
            exit(1)
        print dest
    
        fin = open(source)
        fout = open(dest, 'w')
        for l in fin.readlines():
            l = l.replace("AUTHOR", self.author)
            l = l.replace("DESCRIPTION", self.description)
            l = l.replace("NAMESPACE", self.namespace)
            l = l.replace("MyComponent", self.className)
            l = l.replace("YEAR", str(self.now.year))
            l = l.replace("DATE", "%d %s %d" % (self.now.day, self.now.strftime("%b"), self.now.year))
            fout.write(l)
        fout.close()
        fin.close()

def main():
    """
    Paster for CombLayer
    """

    # get default author name from /etc/passwd:
    defauthor = pwd.getpwuid(os.getuid())[4].split(',')[0]
    
    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('-model', dest='model', type=str, help='model name', required=False, default='ess')
    parser.add_argument('-namespace', dest='namespace', type=str, help='namespace name', required=False, default='essSystem')
    parser.add_argument('-author', dest='author', type=str, help='author', required=False, default=defauthor)
    parser.add_argument('-m', dest='description', type=str, help='class description', required=True)
    parser.add_argument('className', type=str, help='class name')
    args = parser.parse_args()

    path    = os.path.join(os.environ["MCTOOLS"], "common/CombLayer/paster")
    cxxOrig = os.path.join(path, "MyComponent.cxx")
    hOrig   = os.path.join(path, "MyComponent.h")

    p = Paster(args.model, args.className)
    p.setAuthor(args.author)
    p.setNamespace(args.namespace)
    p.setDescription(args.description)
    p.processSource(cxxOrig)
    p.processHeader(hOrig)
    
if __name__ == "__main__":
    exit(main())
