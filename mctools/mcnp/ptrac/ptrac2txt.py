#!/usr/bin/python2 -W all
#
# https://github.com/kbat/mc-tools
#

from __future__ import print_function
import sys, argparse, struct
from os import path
import numpy as np
from mctools.mcnp.ssw import fortranRead

class PTRAC:
        """PTRAC reader for MCNPX
        """
        def __init__(self,fname,verbose=False):
                self.verbose = verbose
                self.fname=fname
                self.file = open(self.fname, 'rb')
                
                data = fortranRead(self.file)
                (i,) =  struct.unpack("=i", data)
                if i!=-1:
                        print("Format error: i=",i)
                        self.file.close()
                        sys.exit(1)
                
                data = fortranRead(self.file)
                (self.header,) = struct.unpack("=60s", data)
                print(self.header)
                
                data = fortranRead(self.file)
                (self.title,) = struct.unpack("=80s", data)
                print(self.title)

                # Input data from the PTRAC card used in the MCNP run
                print("Input data:")
                self.input = []
                data = fortranRead(self.file)
                while len(data) == 40:
                        n = struct.unpack("=10f", data)
                        self.input.append(n)
                        data = fortranRead(self.file)

                # flatten the PTRAC input:
                self.input = [item for sublist in self.input for item in sublist]
                print(self.input)

                # Variable IDs:
                # Number of variables expected for each line type and each event type, i.e NPS line and Event1 and Event2 lines for SRC, BNK, SUR, COL, TER
                # The remaining two variables correspond to the transport particle type (1 for neutron etc. or 0 for multiple particle transport),
                # and whether the output is given in real*4 or real*8
                print("Variable IDs:")
                data = fortranRead(self.file)
                self.vars = struct.unpack("=46i", data)
                print(self.vars, "sum:",sum(self.vars))

                self.ReadEvent()
                
                
        def ReadEvent(self):
                # first NPS line
                print("Event:")
                data = fortranRead(self.file)
                x = struct.unpack("=2i", data) 
                print(x)

                

def main():
	"""
	                PTRAC to TXT converter.
	"""
	parser = argparse.ArgumentParser(description=main.__doc__,
					 epilog="Homepage: https://github.com/kbat/mc-tools")
	parser.add_argument('ptrac', type=str, help='ptrac file name')
	parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')
        
	args = parser.parse_args()
        
	if not path.isfile(args.ptrac):
		print("ptrac2root: File %s does not exist." % args.ptrac, file=sys.stderr)
		return 1
        
	p = PTRAC(args.ptrac,args.verbose)
        p.file.close()

if __name__ == "__main__":
        sys.exit(main())
