#!/usr/bin/env python3
#
# https://github.com/kbat/mc-tools
#

import sys, argparse
from os import path
from mctools.mcnp.ssw import SSW

def main():
    """
    WSSA to ASCII converter.
    The particle type (IPT) and surface number (surface) can be derived as shown below:

    i   = TMath::Nint(TMath::Abs(id/1E+6)); # tmp for particle type
    JGP = -TMath::Nint(i/200.0);            # energy group
    JC  = TMath::Nint(i/100.0) + 2*JGP;     #
    IPT = i-100*JC+200*JGP;                 # particle type: 1=neutron, 2=photon, 3=electron
    wz  = TMath::Sqrt(TMath::Max(0, 1-wx*wx-wy*wy)) * id/TMath::Abs(id) # z-direction cosine
    surface = TMath::Abs(id) % 1000000        # surface crossed
    """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog='Homepage: https://github.com/kbat/mc-tools',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("wssa", type=str, help="file name of SSW card output")
    parser.add_argument("txt",  type=str, nargs="?", help="ASCII file name to convert to", default=None)
    parser.add_argument("-f", "--force", action="store_true", default=False, dest="force", help="overwrite the ASCII file, if exists")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, dest="verbose", help="explain what is being done and print some debug info")

    args = parser.parse_args()

    if not path.isfile(args.wssa):
        sys.exit("ssw2txt: File %s does not exist." % args.wssa, file=sys.stderr)

    fout_name = args.wssa+".txt" if args.txt is None else args.txt

    if path.isfile(fout_name) and not args.force:
        sys.exit("ssw2txt: Can't overwrite %s. Remove it or use the '-f' argument." % fout_name)

    fout = open(fout_name, "w")

    ssw = SSW(args.wssa, args.verbose)

    weightsum=0

    print("history id weight energy time x y z wx wy k", file=fout)

    for i in range(ssw.nevt):
        ssb = ssw.readHit()
        history = ssb[0] # >0 = with collision, <0 = without collision
        id = ssb[1] # surface + particle type + multigroup problem info
        weight = ssb[2]
        weightsum=weightsum+ssb[2]
        energy = ssb[3] # [MeV]
        time = ssb[4] # [shakes]
        x = ssb[5] # [cm]
        y = ssb[6] # [cm]
        z = ssb[7] # [cm]
        wx = ssb[8] # x-direction cosine
        wy = ssb[9] # y-direction cosine
        k = ssb[10] # cosine of angle between track and normal to surface jsu (in MCNPX it is called cs)
        print(history, id, weight, energy, time, x, y, z, wx, wy, k, file=fout)
 
    print("Sum of weights","{:.6f}".format(weightsum),"\nNumber of recorded tracks",ssw.nevt, file=fout) # appending sum of all weights and number of recorded tracks
    
    ssw.file.close()
    fout.close()

if __name__ == "__main__":
	sys.exit(main())
