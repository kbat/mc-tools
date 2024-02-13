#!/usr/bin/env python3
#
# https://github.com/kbat/mc-tools
#

from sys import exit, stderr
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
        self.cxxDir = self.model
        self.hDir   = self.cxxDir+'Inc'
        # generator for variables
        self.cxxGenDir = os.path.join('/'.join(self.cxxDir.split('/')[:-1]), "commonGenerator")
        if not os.path.isdir(self.cxxGenDir):
            self.cxxGenDir = self.cxxDir
        self.hGenDir = self.cxxGenDir + 'Inc'
        print(self.cxxGenDir, self.hGenDir)

        self.now = datetime.now()

    def setAuthor(self, val):
        self.author = val

    def setNamespace(self, val):
        self.namespace = val

    def setDescription(self, val):
        self.description = val

    def processModel(self, source, header):
        dest = os.path.join(self.cxxDir, self.className + ".cxx")
        self.process(source, dest)

        dest = os.path.join(self.hDir, self.className + ".h")
        self.process(header, dest)

    def processGenerator(self, source, header):
        dest = os.path.join(self.cxxGenDir, self.className + "Generator.cxx")
        self.process(source, dest)

        dest = os.path.join(self.hGenDir, self.className + "Generator.h")
        self.process(header, dest)

    def process(self, source, dest):
        """
        Processes file from source to dest
        """

        if os.path.isfile(dest):
            print("File %s exists -> aborting" % dest)
            exit(1)
        print(dest)

        fin = open(source)
        fout = open(dest, 'w')
        for l in fin.readlines():
            l = l.replace("AUTHOR", self.author)
            l = l.replace("DESCRIPTION", self.description)
            l = l.replace("NAMESPACE", self.namespace)
            l = l.replace("MyComponent", self.className)
            l = l.replace("INCDIR", self.hDir)
            l = l.replace("CXXDIR", self.cxxDir)
            l = l.replace("YEAR", str(self.now.year))
            l = l.replace("DATE", "%s %d" % (self.now.strftime("%B"), self.now.year))
            fout.write(l)
        fout.close()
        fin.close()

def main():
    """
    New component paster for CombLayer
    """

    # get default author name from /etc/passwd:
    defauthor = pwd.getpwuid(os.getuid())[4].split(',')[0]

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('-model', dest='model', type=str, help='path to the folder with the .cxx file (e.g. Model/MaxIV/Linac)', required=True)
    parser.add_argument('-namespace', dest='namespace', type=str, help='namespace name', required=True)
    parser.add_argument('-author', dest='author', type=str, help='author', required=False, default=defauthor)
    parser.add_argument('-m', dest='description', type=str, help='class description', required=True)
    parser.add_argument('-t', dest='template', type=str, help='template name', required=False, default="Default", choices=['Default','FrontBackCut'])
    parser.add_argument('--disable-generator', dest='noGenerator', action='store_false', default=True, help='do not create generator for variables')
    parser.add_argument('className', type=str, help='class name')
    args = parser.parse_args()

    path    = os.path.join(os.environ["MCTOOLS"], "mctools/common/CombLayer/paster")
    cxxOrig = os.path.join(path, ("MyComponent-%s.cxx" % args.template))
    hOrig   = os.path.join(path, ("MyComponent-%s.h" % args.template))

    cxxGenOrig = os.path.join(path, ("Generator.cxx"))
    hGenOrig   = os.path.join(path, ("Generator.h"))

    p = Paster(args.model, args.className)
    p.setAuthor(args.author)
    p.setNamespace(args.namespace)
    p.setDescription(args.description)
    p.processModel(cxxOrig, hOrig)
    if args.noGenerator:
        p.processGenerator(cxxGenOrig, hGenOrig)


if __name__ == "__main__":
    exit(main())
