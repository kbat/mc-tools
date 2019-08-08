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
                self.event_type = ('NPS', 'src', 'bnk', 'sur', 'col', 'ter')
                self.varid_descr = {1: "NPS", 2: "Event type of 1st event", 3: "NCL(ICL)", 4: "NSF(JSU)", 5: "JPTAL(1,ITAL)", 6: "TAL(JPTAL(7,ITAL))", 7: "Event type of next event", 8: "NODE", 9: "NSR", 10: "NXS(2,IEX)", 11: "Reaction type", 12: "Surface number", 13: "Angle with surface normal [deg]", 14: "Termination type", 15: "Branch number for this history", 16: "IPT", 17: "NCL(ICL)", 18: "MAT(ICL)", 19: "NCP", 20: "XXX", 21: "YYY", 22: "ZZZ", 23: "UUU", 24: "VVV", 25: "WWW", 26: "ERG", 27: "WGT", 28: "TME"}

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
                input_data = []
                data = fortranRead(self.file)
                while len(data) == 40: # 40=4(float size) * 10 numbers per record
                        n = struct.unpack("=10f", data)
                        input_data.append(map(int,n))
                        data = fortranRead(self.file)

                input_data = [item for sublist in input_data for item in sublist] # flatten the PTRAC input_data

                if self.verbose:
                        print("Input keywords array:",input_data,"; length:",len(input_data))

                self.keywords = self.SetKeywords(input_data) # dictionary of input parameters

                # now let's unpack the data read last in the previous while loop but the data length was not 40:
                # Numbers of variables N_i:
                # Number of variables expected for each line type and each event type, i.e NPS line and Event1 and Event2 lines for SRC, BNK, SUR, COL, TER
                # The remaining two variables correspond to the transport particle type (1 for neutron etc. or 0 for multiple particle transport),
                # and whether the output is given in real*4 or real*8
                N = struct.unpack("=20i", data) # record 4+K
                N = N[0:13] # N14-N20 are not used (page I-2)

                self.single_particle_transport = N[11]
                self.output_type = N[12]

                if self.verbose:
                        print("Numbers of variables:",N, len(N))
                        print("Number of variables on the NPS line:",N[0])  # N1=number of variables on the NPS line (I1, I2, ...)
                        print("Output type: real*%d" % self.output_type)

                if self.output_type != 4:
                        print("Output type: real*%d not supported" % self.output_type)
                        sys.exit(1)

                self.nvars = self.SetNVars(N) # dictionary of number of variables

                # total number of variable IDs:
                Ntot = self.nvars['NPS']+sum(self.nvars['src'])+sum(self.nvars['bnk'])+sum(self.nvars['sur'])+sum(self.nvars['col'])+sum(self.nvars['ter'])

                # Variable IDs (record 5+K):
                data = fortranRead(self.file)
                self.vars = struct.unpack("=%di" % Ntot, data)
                self.varid = self.SetVarID(self.vars) # dictionary of variable IDs (L2, L3, etc on pages I-1 and I-2)
                print("Variable IDs:",self.varid)

        def ReadEvent(self):
                # first NPS line
                data = fortranRead(self.file)
                if data is None:
                        return False

                print("Event:")
                I1 = struct.unpack("=%di" % self.nvars['NPS'], data)
                etype = self.GetEventType(I1[1])
                print("NPS:",I1[0], "Event type: %d (%s)" % (I1[1],etype))

                while True: # reading event lines
                        data = fortranRead(self.file)
                        next_etype=self.GetNextEventType(data)
#                        print("next:",next_etype)
                        # Event line:
                        JP = struct.unpack("=%df%df" % self.nvars[etype], data) # table I-1: J and P values are explained in table I-3
                        print(etype,JP)
                        
                        self.PrintEventLine(etype,JP)

                        etype=next_etype
                        if next_etype is 'Flag':
                                return True

                print("self.ReadEvent: problems with reading event (the code should not reach this line)")
                sys.exit(1)

        def PrintEventLine(self,etype,JP):
                """ Print event line """
                print(" J1:",self.varid_descr[7],JP[0]);
                print(" J2:",self.varid_descr[8],JP[1]);
                
                if self.GetEventLineType() == 1:
                        if etype=='src':
                                print(" J3:",self.varid_descr[9],JP[2]);
                                print(" J4:",self.varid_descr[17],JP[3]);
                                print(" J5:",self.varid_descr[18],JP[4]);
                                print(" P1:",self.varid_descr[20],JP[5]);
                                print(" P2:",self.varid_descr[21],JP[6]);
                                print(" P3:",self.varid_descr[22],JP[7]);
                        else:
                                print(" J3: NXS(2,IEX):",JP[2]);
                                print(" J4: Recation type (see table I-7):",JP[3]);
                                print(" J5: NCL(ICL):",JP[4]);
                                print(" J6: MAT(ICL):",JP[5]);
                                print(" P1:",self.varid_descr[20],JP[6]);
                                print(" P2:",self.varid_descr[21],JP[7]);
                                print(" P3:",self.varid_descr[22],JP[8]);

        def GetEventType(self,I2):
                """ Return event type for the given event
                    See table I-5 on page I-6
                """
                if I2 == 1000:
                        return 'src'
                elif I2 == 3000:
                        return 'sur'
                elif I2 == 4000:
                        return 'col'
                elif I2 == 5000:
                        return 'ter'
                elif I2 == 9000:
                        return 'Flag'

        def GetNextEventType(self, data):
                """ Guess the data type based on its int (table I-5 on page I-6) """
                length = len(data)
                if not length%2: # even
                        d = struct.unpack("=%df" % (length/self.output_type), data)
                        return self.GetEventType(int(d[0]))
                else:            # odd
                        print("[self.NextEventType] odd: not implemented yet")
                        sys.exit(1)

        def GetEventLineType(self):
                """ Return event line type according to Table I-3 """
                if self.keywords['write'] == [1]:
                        return 1 if self.single_particle_transport else 0
                else:
                        print("Not implemented yet")
                        sys.exit(1)
                        # if self.nvars['src'] == (5,3):
                        #         print("event line type :1");
                
        def SetKeywords(self,data):
                # set the input parameters keywords
                # see pages 5-205 and I-3 of the MCNPX manual
                kwdlist = ('buffer', 'cell', 'event', 'file', 'filter', 'max', 'meph', 'nps', 'surface', 'tally', 'type', 'value', 'write')

                j = 1 # position of n_i
                n = 0 # number of entries for the i-th keyword or 0 for no entries
                keywords = {}
                for i,k in enumerate(kwdlist):
                        n = data[j]
                        i1 = 1+j
                        i2 = i1+n
                        if n:
                                keywords[k] = data[i1:i2]
                        j=i2

                if self.verbose:
                        print("Number of PTRAC keywords:", data[0])
                        print("Input keywords dict: ",keywords)
                return keywords

        def SetNVars(self,data):
                """ Set number of variables on the corresponding event lines (page I-2)"""
                i=0
                nvars = {}
                for t in self.event_type:
                        if i == 0:
                                nvars[t] = data[i]
                                i = i+1
                        else:
                                nvars[t] = data[i:i+2]
                                i = i+2

                if self.verbose:
                        print("Number of variables on the event lines:",nvars)
                return nvars

        def SetVarID(self,data):
                """ Set variable IDs L1, L2, L3 etc """
                i = 0
                L = {}
                for t in self.event_type:
                        if t == 'NPS':
                                j = i+self.nvars[t]
                        else:
                                j = i+sum(self.nvars[t])
                        L[t] = data[i:j]
                        i=j
                return L
                

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
        while p.ReadEvent():
                pass
        p.file.close()

if __name__ == "__main__":
        sys.exit(main())
