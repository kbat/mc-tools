#include <iostream>

#include <TDirectory.h>
#include <TCanvas.h>
#include "DynamicSlice.h"

DynamicSlice::DynamicSlice(const std::vector<unsigned short>& slice) :
  h2(nullptr), nbins(slice[0]), ngroup(slice[1]), projection(kTRUE), logy(kFALSE),
  range(0.0, 0.0), old(0, 0)
{

}

void DynamicSlice::Draw(const std::shared_ptr<TH2> h2,
			TVirtualPad *h2pad,
			TVirtualPad *slicepad)
{
  // if ((!h2) || (!h2.get()->InheritsFrom(TH2::Class())))
  //   return;

  if (gPad!=h2pad)
    return;

  pad = slicepad;

  h2pad->GetCanvas()->FeedbackMode(kTRUE);
  Int_t event = h2pad->GetEvent();
  if (event==kButton1Down)
    projection = !projection;
  else if (event == kButton2Up)
    logy = !logy;

  const Int_t px = h2pad->GetEventX();
  const Int_t py = h2pad->GetEventY();

  const Double_t uxmin = h2pad->GetUxmin();
  const Double_t uxmax = h2pad->GetUxmax();
  const Double_t uymin = h2pad->GetUymin();
  const Double_t uymax = h2pad->GetUymax();

  const Int_t pxmin = h2pad->XtoAbsPixel(uxmin);
  const Int_t pxmax = h2pad->XtoAbsPixel(uxmax);
  const Int_t pymin = h2pad->YtoAbsPixel(uymin);
  const Int_t pymax = h2pad->YtoAbsPixel(uymax);

  const Double_t scaleX = abs((pxmax-pxmin) / (uxmax-uxmin));
  const Double_t scaleY = abs((pymax-pymin) / (uymax-uymin));

  Double_t width = 0.0; // arbitrary default value [cm]
  if ((old.first > 0.0) || (old.second>0.0))
    width = range.second - range.first;

  Int_t ywidth = floor(width*scaleY);
  Int_t xwidth = floor(width*scaleX);

  if ((old.first > 0.0) || (old.second>0.0)) {
      if (projection) {
	gVirtualX->DrawLine( pxmin, old.second, pxmax, old.second);
	gVirtualX->DrawLine( pxmin, old.second-ywidth, pxmax, old.second-ywidth);
      } else {
	gVirtualX->DrawLine( old.first, pymin, old.first, pymax);
	gVirtualX->DrawLine( old.first+xwidth, pymin, old.first+xwidth, pymax);
      }
  }

  if (projection)
    h2pad->SetUniqueID(py);
  else
    h2pad->SetUniqueID(px);

  old = {px, py};

  const Double_t upx = h2pad->AbsPixeltoX(px);
  Double_t x = h2pad->PadtoX(upx);

  const Double_t upy = h2pad->AbsPixeltoY(py);
  Double_t y = h2pad->PadtoY(upy);

  if (projection)
    range = DrawSlice(h2, y, "Y");
  else
    range = DrawSlice(h2, x, "X");

  h2pad->cd();

  return;
}

std::pair<double, double> DynamicSlice::DrawSlice(const std::shared_ptr<TH2> histo,
						  const Int_t value, const std::string& xy)
{
  const std::string yx = xy == "X" ? "Y" : "X";
  const std::string vert_axis = yx;

  pad->SetGrid();
  pad->cd();

  const TAxis *axis = xy == "X" ? histo->GetXaxis() : histo->GetYaxis();
  const Int_t bin1 = axis->FindBin(value);
  const Int_t bin2 = bin1+nbins-1;
  const Double_t vmin = axis->GetBinLowEdge(bin1);
  const Double_t vmax = axis->GetBinUpEdge(bin2);

  char *hname = Form("Projection%s",xy.data());
  TH1 *hp = yx == "X" ? histo->ProjectionX(hname, bin1, bin2) : histo->ProjectionY(hname, bin1, bin2);
  hp->SetFillColor(38);
  hp->SetLineWidth(2);
  hp->SetFillStyle(3001);
  hp->SetLineColor(kBlack);

  hname = Form("%s Projection of %ld %s bins: %g < %s < %g (#Delta %s = %g)", xy.data(), nbins, vert_axis.data(), vmin, vert_axis.data(), vmax, vert_axis.data(), vmax-vmin);
  hp->SetTitle(hname);

  if (ngroup>=1)
    hp->Rebin(ngroup);

  if ((nbins>1) || (ngroup>=1))
    hp->Scale(1.0/(nbins*ngroup));

  hp->Draw("hist,e");
  TAxis *yaxis = hp->GetYaxis();
  yaxis->SetMaxDigits(3);
  yaxis->SetTitle(histo->GetZaxis()->GetTitle());
  pad->SetLogy(logy);

  pad->Update();

  return {vmin, vmax};
}
