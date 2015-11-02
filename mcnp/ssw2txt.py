#! /usr/bin/python
# $Id$
# $URL$

import sys, argparse
from ssw import SSW

def main():
    """
    Converts SSW binary to ASCII.
    The particle type (IPT) and surface number (surface) can be derived as shown below:

    i   = TMath::Nint(TMath::Abs(id/1E+6)); # tmp for particle type
    JGP = -TMath::Nint(i/200.0);            # energy group
    JC  = TMath::Nint(i/100.0) + 2*JGP;     #
    IPT = i-100*JC+200*JGP;                 # particle type: 1=neutron, 2=photon, 3=electron
    wz  = TMath::Sqrt(TMath::Max(0, 1-wx*wx-wy*wy)) * id/TMath::Abs(id) # z-direction cosine
    surface = TMath::Abs(id) % 1000000        # surface crossed
    """

    allowed_splitlevels = (1, 99)
    parser = argparse.ArgumentParser(description=main.__doc__, epilog='Homepage: https://github.com/kbat/mc-tools', formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('wssa', type=str, help='ssw output file name')
    arguments = parser.parse_args()

    fin_name = arguments.wssa
    fout_name = fin_name + ".root"

    ssw = SSW(fin_name)

    print "history id weight energy time x y z wx wy k"

    for i in range(ssw.nevt):
        ssb = ssw.readHit()
        history = ssb[0] # >0 = with collision, <0 = without collision
        id = ssb[1] # surface + particle type + multigroup problem info
        weight = ssb[2]
        energy = ssb[3] # [MeV]
        time = ssb[4] # [shakes]
        x = ssb[5] # [cm]
        y = ssb[6] # [cm]
        z = ssb[7] # [cm]
        wx = ssb[8] # x-direction cosine
        wy = ssb[9] # y-direction cosine
        k = ssb[10] # cosine of angle between track and normal to surface jsu (in MCNPX it is called cs)
        print history, id, weight, energy, time, x, y, z, wx, wy, k


if __name__ == "__main__":
	sys.exit(main())
