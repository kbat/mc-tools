#!/usr/bin/env python3
import sys, argparse, re
from os import path

def read(opt,dtl,start,end):
    """ Read the optics file """

    pmqBase = dtl + "PMQ"

    f = open(opt)
    val = 0.0
    iPMQ = int(1)
    found = False
    for l in f:
        if re.search(start,l):
            found = True
        if found:
            val = float(l.split()[4])*100.0
            var = "%s%dLength" % (pmqBase, iPMQ)
            print("  Control.addVariable(\"%s\",%g);" % (var,val))
            # read the next line with GapLength
            l = f.readline()
            val = float(l.split()[4])*100.0
            var = "%s%dGapLength" % (pmqBase, iPMQ)
            print("  Control.addVariable(\"%s\",%g);" % (var,val))

        if found:
            iPMQ += 1

        if found and re.search(end,l):
#            stop = True
            break

    f.close()
#    print("  Control.addVariable(\"%sPMQ%dMat5\", \"SS304L\");" % (dtl,iPMQ-1)) # last half
    print("  Control.addVariable(\"%sNPMQ\",%d);" % (dtl,iPMQ-1))
    print("  Control.addVariable(\"%sPMQ%dMat5\",\"SS304L\");" % (dtl,iPMQ-1))
    print("")


def printHead(args):
    """ Print the section with #includes """
    print("// This file is generated by the 'optics2var' script from the optics file.")
    print("//",args)
    print("""
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <cmath>
#include <complex>
#include <list>
#include <vector>
#include <set>
#include <map>
#include <string>
#include <algorithm>
#include <iterator>
#include <memory>

#include "Exception.h"
#include "FileReport.h"
#include "NameStack.h"
#include "RegMethod.h"
#include "GTKreport.h"
#include "OutputLog.h"
#include "support.h"
#include "stringCombine.h"
#include "MatrixBase.h"
#include "Matrix.h"
#include "Vec3D.h"
#include "Code.h"
#include "varList.h"
#include "FuncDataBase.h"
#include "variableSetup.h"

namespace setVariable
{
void
EssLinacPMQVariables(FuncDataBase &Control)
  /*!
    Create all the PMQ variables
    \param Control :: DataBase
  */
{
  ELog::RegMethod RegA("essVariables[F]","EssLinacPMQVariables");
""")

def printTail():
    """ Print the closing brackets in the end """
    print("""  return;
}
}
    """)

def main():
    """ Convert optics file into C++ code with CombLayer variables """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('opt', type=str, help='optics file name')
    parser.add_argument('-dtl', type=str, help='DTL name (e.g. LinacDTL1)', required=True)
    parser.add_argument('-start', type=str, help='first record (e.g. quad1213)', required=True)
    parser.add_argument('-end', type=str, help='last record (e.g. D204US)')

    args = parser.parse_args()

    if not path.isfile(args.opt):
        print("optics2var: Can't open %s" % args.opt, file=sys.stderr)
        return 1

    printHead(args)
    read(args.opt, args.dtl, args.start, args.end)
    read(args.opt, "LinacDTL2", "quad137", "D276US") # q_flg_DTL_US -> flg_DTL
    read(args.opt, "LinacDTL3", "quad209", "D340US")
    read(args.opt, "LinacDTL4", "quad273", "D396US")
    read(args.opt, "LinacDTL5", "quad329", "D442US")

    for i in range(6,51):
            read(args.opt, "LinacDTL%d" % i, "quad329", "D442US")

    printTail()

if __name__ == "__main__":
    sys.exit(main())
