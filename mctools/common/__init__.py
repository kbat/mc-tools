__all__ = [ "ascii2gr", "ascii2th1", "ascii2th3", "mixtures" ]

import ROOT

def FlipTH2(h):
    """ Flip the TH2 along the Y axis """
    flipped = h.Clone(h.GetName()+"_flipped")
    flipped.Reset()

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

def ErrorHist(h):
    """ Return TH2 histogram of errors """

    herr = h.Clone(h.GetName()+"_err")
    herr.Reset()

    nx = h.GetNbinsX()
    ny = h.GetNbinsY()
    for i in range(1,nx+1):
        for j in range(1,ny+1):
            val = h.GetBinContent(i,j)
            if val != 0:
                err = h.GetBinError(i,j) / h.GetBinContent(i,j)
            else:
                err = 0.0
            herr.SetBinContent(i,ny+1-j,err)

    herr.GetZaxis().SetTitle("Relative error");
    return herr
