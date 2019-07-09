__all__ = [ "ascii2gr", "ascii2th1", "ascii2th3", "mixtures" ]

import ROOT

def FlipTH2(h):
    """ Flip the TH2 along the Y axis """
    flipped = h.Clone()
    flipped.Reset()
    flipped.SetName(h.GetName()+"_flipped")

    nx = h.GetNbinsX()
    ny = h.GetNbinsY()
    for i in range(1,nx+1):
        for j in range(1,ny+1):
            val = h.GetBinContent(i,j)
            err = h.GetBinError(i,j)
            flipped.SetBinContent(i,ny+1-j,val)
            flipped.SetBinError(i,ny+1-j,err)

    # also flip the Y axis
    AAxis=flipped.GetYaxis()
    AAxis.Set(AAxis.GetNbins(), -AAxis.GetXmax(), -AAxis.GetXmin())

    return flipped
