#include <iostream>

#include <TDirectory.h>
#include <TCanvas.h>
#include "DynamicSlice.h"

DynamicSlice::DynamicSlice(const std::vector<unsigned short>& slice) :
  h2(nullptr), nbins(slice[0]), ngroup(slice[1]), projection(kTRUE), logy(kFALSE),
  range(0.0, 0.0), old(0, 0), cX(nullptr), cY(nullptr)
{

}

void DynamicSlice::DestroyPrimitive(const std::string& xy)
/*!
  Delete projected histogram
 */
{
  const TH2* proj = dynamic_cast<TH2*>((xy == "X" ? cX : cY)->GetPrimitive(("Projection"+xy).c_str()));
  if (proj) {
    delete proj;
    proj = nullptr;
  }
}

void DynamicSlice::call(const std::shared_ptr<TH2> h2)
{
  // if ((!h2) || (!h2.get()->InheritsFrom(TH2::Class())))
  //   return;

  gPad->GetCanvas()->FeedbackMode(kTRUE);
  Int_t event = gPad->GetEvent();
  if (event==kButton1Down)
    projection = !projection;
  else if (event == kButton2Up)
    logy = !logy;

  const Int_t px = gPad->GetEventX();
  const Int_t py = gPad->GetEventY();

  const Double_t uxmin = gPad->GetUxmin();
  const Double_t uxmax = gPad->GetUxmax();
  const Double_t uymin = gPad->GetUymin();
  const Double_t uymax = gPad->GetUymax();

  const Int_t pxmin = gPad->XtoAbsPixel(uxmin);
  const Int_t pxmax = gPad->XtoAbsPixel(uxmax);
  const Int_t pymin = gPad->YtoAbsPixel(uymin);
  const Int_t pymax = gPad->YtoAbsPixel(uymax);

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
    gPad->SetUniqueID(py);
  else
    gPad->SetUniqueID(px);

  old = {px, py};

  const Double_t upx = gPad->AbsPixeltoX(px);
  Double_t x = gPad->PadtoX(upx);

  const Double_t upy = gPad->AbsPixeltoY(py);
  Double_t y = gPad->PadtoY(upy);

  TVirtualPad *padsav = gPad;

  // create or set the display canvases
  if (!cX)
    cX = gPad->GetCanvas()->GetPad(2);
  else
    DestroyPrimitive("X");

  if (!cY)
    cY = gPad->GetCanvas()->GetPad(2);
  else
    DestroyPrimitive("Y");

  if (projection)
    range = DrawSlice(h2, y, "Y");
  else
    range = DrawSlice(h2, x, "X");

  padsav->cd();

  return;
}

std::pair<double, double> DynamicSlice::DrawSlice(const std::shared_ptr<TH2> histo,
						  const Int_t value, const std::string& xy)
{
  const std::string yx = xy == "X" ? "Y" : "X";
  const std::string vert_axis = yx;

  TVirtualPad *canvas = xy == "X" ? cX : cY;
  canvas->SetGrid();
  canvas->cd();

  const TAxis *axis = xy == "X" ? histo->GetXaxis() : histo->GetYaxis();
  const Int_t bin1 = axis->FindBin(value);
  const Int_t bin2 = bin1+nbins-1;
  const Double_t vmin = axis->GetBinLowEdge(bin1);
  const Double_t vmax = axis->GetBinUpEdge(bin2);

  const char *hname = ("Projection"+xy).c_str();
  TH1 *hp = yx == "X" ? histo->ProjectionX(hname, bin1, bin2) : histo->ProjectionY(hname, bin1, bin2);
  hp->SetFillColor(38);
  hp->SetLineWidth(2);
  hp->SetFillStyle(3001);
  hp->SetLineColor(kBlack);

  hp->SetTitle("title");

  if (ngroup>=1)
    hp->Rebin(ngroup);

  if ((nbins>1) || (ngroup>=1))
    hp->Scale(1.0/(nbins*ngroup));

  hp->Draw("hist,e");
  TAxis *yaxis = hp->GetYaxis();
  yaxis->SetMaxDigits(3);
  yaxis->SetTitle(histo->GetZaxis()->GetTitle());
  canvas->SetLogy(logy);

  canvas->Update();
  return {vmin, vmax};
}
