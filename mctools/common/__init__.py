__all__ = [ "ascii2gr", "ascii2th1", "ascii2th3", "mixtures" ]

import ROOT

def ReverseYAxis(h,loffset=-0.05):
    """ Reverse y axis of the given histogram """
    oldaxis = h.GetYaxis()
    oldaxis.SetLabelOffset(999);
    oldaxis.SetTickLength(0);

    pad = ROOT.gPad;
    pad.Update()
    newaxis = ROOT.TGaxis(pad.GetUxmin(), pad.GetUymax(), pad.GetUxmin()-1, pad.GetUymin(), oldaxis.GetXmin(), oldaxis.GetXmax(), 510, "+L")
    newaxis.SetLabelOffset(loffset)

    newaxis.SetLabelFont(oldaxis.GetLabelFont())
    newaxis.SetLabelSize(oldaxis.GetLabelSize())
    return newaxis

def FlipTH2(h):
    """ Flip the TH2 along the Y axis """
    flipped = h.Clone()
    flipped.Reset()
    flipped.SetName(h.GetName()+"_flipped")

    nx = h.GetNbinsX()
    ny = h.GetNbinsY()
    print(flipped.GetName(),nx,ny)
    for i in range(1,nx+1):
        for j in range(1,ny+1):
            val = h.GetBinContent(i,j)
            err = h.GetBinError(i,j)
            flipped.SetBinContent(i,ny+1-j,val)
            flipped.SetBinError(i,ny+1-j,err)

    return flipped
