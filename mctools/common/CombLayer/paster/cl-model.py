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

class Model:
    def __init__(self, p, m, t):
        """New model Constructor"""
        self.model = m
        self.template = t
        self.cxxDir = os.path.join(p, m.lower()+"Build")
        self.hDir   = self.cxxDir+'Inc'
        self.variables = os.path.join(self.cxxDir, m.lower()+"Variables.cxx")
        self.makeCXX = os.path.join(self.cxxDir, f"make{m}.cxx")
        self.makeH = os.path.join(self.hDir, f"make{m}.h")
        self.now = datetime.now()

        paster = os.path.join(os.environ["MCTOOLS"], "mctools/common/CombLayer/paster")
        self.templateCXX = os.path.join(paster, ("makeMyModel-%s.cxx" % self.template))
        self.templateH   = os.path.join(paster, ("makeMyModel-%s.h" % self.template))
        self.templateVariables   = os.path.join(paster, "MyModelVariables.cxx")

        if not os.path.exists(self.cxxDir):
            os.makedirs(self.cxxDir)
        if not os.path.exists(self.hDir):
            os.makedirs(self.hDir)

    def print(self):
        # print("Path:",self.path)
        # print("Model:",self.model)
        print("cxxDir:",self.cxxDir)
        print("hDir:  ",self.hDir)
        print("variables:  ",self.variables)
        print("make:  ",self.makeCXX, self.makeH)

    def setAuthor(self, val):
        self.author = val

    def setNamespace(self, val):
        self.namespace = val

    def setDescription(self, val):
        self.description = val

    def processAll(self):
        self.process(self.templateCXX, self.makeCXX)
        self.process(self.templateH, self.makeH)
        self.process(self.templateVariables, self.variables)

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
            l = l.replace("MODEL", self.model)
            l = l.replace("INCDIR", self.hDir)
            l = l.replace("CXXDIR", self.cxxDir)
            l = l.replace("YEAR", str(self.now.year))
            l = l.replace("DATE", "%s %d" % (self.now.strftime("%B"), self.now.year))
            fout.write(l)
        fout.close()
        fin.close()

def main():
    """
    New model paster for CombLayer
    """

    # get default author name from /etc/passwd:
    defauthor = pwd.getpwuid(os.getuid())[4].split(',')[0]

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('-path', dest='path', type=str, help='path to the container directory for the header and implementation folders, e.g. Model)', required=True)
    parser.add_argument('-namespace', dest='namespace', type=str, help='namespace name', required=True)
    parser.add_argument('-author', dest='author', type=str, help='author', required=False, default=defauthor)
    parser.add_argument('-m', dest='description', type=str, help='model description', required=True)
    parser.add_argument('-t', dest='template', type=str, help='template name', required=False, default="Default", choices=['Default'])
    parser.add_argument('model', type=str, help='new model name')

    args = parser.parse_args()

    m = Model(args.path, args.model, args.template)

    m.setAuthor(args.author)
    m.setNamespace(args.namespace)
    m.setDescription(args.description)
    m.print()

    m.processAll()


if __name__ == "__main__":
    exit(main())
