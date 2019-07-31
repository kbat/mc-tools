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
                self.keywords = {} # dictionary of input parameters
                
                data = fortranRead(self.file)
                (i,) =  struct.unpack("=i", data)
                if i!=-1:
                        print("Format error: i=",i)
                        self.file.close()
                        sys.exit(1)
                
                data = fortranRead(self.file)
                (self.code,self.ver,self.loddat,self.idtm,self.rundat)=struct.unpack("=8s5s11s19s17s", data)
                
                self.code = self.code.strip()
                self.ver  = self.ver.strip()
                self.loddat = self.loddat.strip()
                self.idtm = self.idtm.strip()
                self.rundat = self.rundat.strip()

                data = fortranRead(self.file)
                (self.title,) = struct.unpack("=80s", data)
                self.title = self.title.strip()

                if verbose:
                        print("code:    ", self.code)
                        print("ver:     ", self.ver)
                        print("loddat:  ", self.loddat)
                        print("idtm:    ", self.idtm)
                        print("run date:", self.rundat)
                        print("title:   ", self.title)

                # Input data from the PTRAC card used in the MCNPX run
                print("Input data:")
                input_data = []
                data = fortranRead(self.file)
                while len(data) == 40:
                        n = struct.unpack("=10f", data)
                        input_data.append(map(int,n))
                        data = fortranRead(self.file)

                # flatten the PTRAC input_data:
                input_data = [item for sublist in input_data for item in sublist]
                print(input_data,len(input_data))

                self.SetKeywords(input_data)

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

        def SetKeywords(self,data):
                # set the input parameters keywords
                # see pages 5-205 and I-3 of the MCNPX manual
                self.keywords['buffer']  = data[1]
                self.keywords['cell']    = data[2]
                self.keywords['event']   = data[3]
                self.keywords['file']    = data[4]
                self.keywords['filter']  = data[5]
                self.keywords['max']     = data[6]
                self.keywords['menp']    = data[7]
                self.keywords['nps']     = data[8]
                self.keywords['surface'] = data[9]
                self.keywords['tally']   = data[10]
                self.keywords['type']    = data[11]
                self.keywords['value']   = data[12]
                self.keywords['write']   = data[13]
                

def main():
	"""
	PTRAC to TXT converter.

        Assumes that the PTRAC file is generated by MCNPX in binary format.
	"""
	parser = argparse.ArgumentParser(description=main.__doc__,
					 epilog="Homepage: https://github.com/kbat/mc-tools")
	parser.add_argument('ptrac', type=str, help='ptrac binary file name')
	parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')
        
	args = parser.parse_args()
        
	if not path.isfile(args.ptrac):
		print("ptrac2txt: File %s does not exist." % args.ptrac, file=sys.stderr)
		return 1
        
	p = PTRAC(args.ptrac,args.verbose)
        p.file.close()

if __name__ == "__main__":
        sys.exit(main())
