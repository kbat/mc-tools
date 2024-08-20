#!/usr/bin/env python3

import sys, argparse, os, struct
from array import array
from mctools.fluka.flair import fortran
from mctools.fluka import particle
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

class Reader:
    def __init__(self, fname, verbose):
        self.first = True
        self.fname = fname
        self.f = open(self.fname, 'rb')
        self.verbose = verbose

        self.iread = 0
        self.readTitleTime()
        self.iread += 1
        self.ib0 = 0
        self.nbtot = 0 # total number of binnings

        self.lntzer = None

        ib=self.ib0+1
        while True:
            data = self.read(False)
            if data is None:
                break
            size = len(data)
            if size != 90:
                break

            mb,titusb,itusbn,idusbn, \
                xlow,xhigh,nxbin,dxusbn, \
                ylow,yhigh,nybin,dyusbn, \
                zlow,zhigh,nzbin,dzusbn, \
                self.lntzer,bkusbn,b2usbn,tcusbn,tmp = struct.unpack("=i10s2i2fi3fi3fifi3fi",data)
            titusb = titusb.decode('utf8').strip() # estimator title

            print(f"binning number: {mb}, title: {titusb}, type: {itusbn}")
            print(f"\tdistribution to be scored: {particle[idusbn]}")
            print(f"\tx-axis: ",xlow,xhigh,nxbin,dxusbn)
            print(f"\ty-axis: ",ylow,yhigh,nybin,dyusbn)
            print(f"\tz-axis: ",zlow,zhigh,nzbin,dzusbn)
            print(f"\tsave non-zero scores only: {bool(self.lntzer)}")
            print(f"\tBirk's law parameters: {bkusbn} {b2usbn}")
            print(f"\tTime cut-off: {tcusbn} sec")
            print(f"\tpad byte??? (then unpack it as '4x'): {tmp}")

            self.iread += 1
            self.nbtot=ib

        print("seek 0")
        self.f.seek(0)

        for i in range(self.iread):
            data = self.read(True)

        print("here1")

        # a,b,c,d = struct.unpack("=iiff",data)
        # print(a,b,c,d)

#        data = self.read(True)

    def readEvent(self):
        print("\n*** reading an event")
        iev = 1

        etot = 0.0
        etot1 = 0.0
        numhits = 0.0
        hits = {}
        for ib in range(self.nbtot): # loop over detectors
            print("*** here ib:",ib)
            data = self.read(not True)
            if data is None:
                return False
            mb,ievd,wei,tmp = struct.unpack("=iifi",data)
            print(mb,ievd,wei,tmp)
            nb = ib

            if self.lntzer:
                print("not lntzer")
                data = self.read()
                size = len(data)
                nhits = struct.unpack("=i",data[:4])[0]
                assert(nhits==(size-4)//8) # just a quick format check
                vals = struct.unpack("=%s" % ("if"*nhits), data[4:]) # ihelp, gmhelp
                etot = 0.0
                for i in range(0, nhits*2, 2):
                    hits[vals[i]] = vals[i+1] # global bin number -> value pair
                    etot += vals[i+1]
                print(hits)
                print("Number of hits in this event:", nhits)
                print("Edep in this event:", etot)
            else: # all cells are dumped
                print("TODO: Implement the case where all cells are dumped")
                pass
        return True


    def __del__(self):
        self.f.close()

    def read(self, debug=False):
        data = fortran.read(self.f)
        if debug:
            size = len(data)
            print("size: ", size)
        return data

    def readTitleTime(self):
        if not self.first:
            return False
        self.first = False

        data = fortran.read(self.f)
        title, time = struct.unpack("=80s32s", data)
        title = title.decode('utf8').strip()
        time = time.decode('utf8').strip()
        if self.verbose:
            print(title,time)


def main():
    """ Converts EVENTBIN output into a ROOT TTree """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('eventbin', type=str, nargs='*', help='list of EVENTBIN files')
    parser.add_argument('-o', dest='root', type=str, help='output ROOT file name', default="")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='print what is being done')
    parser.add_argument('-f', '--force', action='store_true', default=False, dest='overwrite', help='overwrite the output ROOT file')


    args = parser.parse_args()

    for f in args.eventbin:
        if not os.path.isfile(f):
            print("eventbin2root: File %s does not exist." % f, file=sys.stderr)
            return 1

    if not args.overwrite and os.path.isfile(args.root):
        sys.exit("%s exists. Use '-f' to overwrite it." % args.root)

    first = True
    for eventbin in args.eventbin:
        data = Reader(eventbin, args.verbose)
        ievent = 0
        while data.readEvent() != False:
            ievent += 1
            print("event ", ievent)
    return 0


        # with open(eventbin, 'rb') as f:
        #     print(eventbin)
        #     data = fortran.read(f)
        #     title, time = struct.unpack("=80s32s", data)
        #     title = title.decode('utf8').strip()
        #     time = time.decode('utf8').strip()
        #     print(time)

        #     while True:
        #         data = fortran.read(f)
        #         size = len(data)
        #         print("size:",size)
        #         if data is None:
        #             break

        #         if first:
        #             first = False

        #         mb,titusb,itusbn,idusbn, \
        #             xlow,xhigh,nxbin,dxusbn, \
        #             ylow,yhigh,nybin,dyusbn, \
        #             zlow,zhigh,nzbin,dzusbn, \
        #             lntzer,bkusbn,b2usbn,tcusbn,tmp = struct.unpack("=i10s2i2fi3fi3fifi3fi",data)
        #         titusb = titusb.decode('utf8').strip() # estimator title

        #         print(mb,titusb,itusbn,idusbn,xlow,xhigh,nxbin,dxusbn,ylow,yhigh,nybin,dyusbn,zlow,zhigh,nzbin,dzusbn,lntzer,bkusbn,b2usbn,tcusbn,tmp)

        #         data = fortran.read(f)
        #         size = len(data)
        #         print("size:",size)
        #         a,b,c,d = struct.unpack("=iifi",data)
        #         print(a,b,c,d)

        #         data = fortran.read(f)
        #         size = len(data)
        #         print("size:",size)


        #         break

#                    title, time, nregs, nsco, dist = struct.unpack("=80s32siii", data)

            #         print("title:", title)
            #         print("time:", time)
            #         print("number of regions:",nregs)
            #         print("number of scoring distributions:", nsco)
            #         print("distribution:",dist)

            #         DATA = array('f', nsco*nregs*[0.0])

            #         fout = ROOT.TFile(args.root, "recreate", title)
            #         T = ROOT.TTree("EVENTBIN", time)
            #         T.Branch("DATA", DATA, "d%d[%d]/F" % (dist,nsco*nregs))
            #     elif size == 12:
            #         pass
            #     elif size == 48:
            #         pass
            #     elif size == 8:
            #         pass
            #     elif size == nregs*nsco*4:
            #         val = struct.unpack("%df" % nregs*nsco, data)
            #         for i,v in enumerate(val):
            #             DATA[i] = v
            #         T.Fill()

    # T.Write()
    # fout.Close()


if __name__=="__main__":
    sys.exit(main())
