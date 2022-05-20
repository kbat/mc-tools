#include <iostream>

#include <TDirectory.h>
#include <TCanvas.h>
#include <TF1.h>
#include "Profile.h"

Profile::Profile(const std::shared_ptr<Data3> data) :
  h2(nullptr), data(data), hprofile(nullptr), logy(kFALSE)
{
  const TAxis *axis = data->GetNormalAxis();
  const Int_t nbins = axis->GetNbins();
  std::vector<double> edges;
  edges.reserve(nbins+1);
  //  axis->GetLowEdge(edges);
  for (int i=0; i<nbins+1; ++i)
    edges.push_back(axis->GetBinLowEdge(i+1));

  for (int i=1; i<5; ++i)
    std::cout << edges[i-1] << " ";
  std::cout << "\t";
  for (int i=nbins-5; i<=nbins+1; ++i)
    std::cout << axis->GetBinLowEdge(i) << " ";
  std::cout << std::endl;

  std::cout << nbins << " "  << edges.size() << std::endl;
  hprofile = std::make_shared<TH1F>("hp", "htitle", nbins, edges.data());
  hprofile->SetFillColor(38);
  hprofile->SetLineWidth(2);
  hprofile->SetFillStyle(3001);
  hprofile->SetLineColor(kBlack);
}

void Profile::Draw(const std::shared_ptr<TH2> h2,
		   TVirtualPad *h2pad,
		   TVirtualPad *profilepad)
{
  // if ((!h2) || (!h2.get()->InheritsFrom(TH2::Class())))
  //   return;

  if (gPad!=h2pad)
    return;

  pad = profilepad;

  h2pad->GetCanvas()->FeedbackMode(kTRUE);
  Int_t event = h2pad->GetEvent();
  if (event == kButton2Up)
    logy = !logy;

  const Int_t px = h2pad->GetEventX();
  const Int_t py = h2pad->GetEventY();


  h2pad->SetUniqueID(py);

  const Double_t upx = h2pad->AbsPixeltoX(px);
  Double_t binx = h2pad->PadtoX(upx);

  const Double_t upy = h2pad->AbsPixeltoY(py);
  Double_t biny = h2pad->PadtoY(upy);

  DrawProfile(h2, binx, biny);

  h2pad->cd();

  return;
}

void Profile::DrawProfile(const std::shared_ptr<TH2> histo,
			  const Int_t x,
			  const Int_t y)
{
  pad->SetGrid();
  pad->cd();

  const auto h3 = data->GetH3();

  Int_t biny = data->GetHorizontalAxis()->FindBin(x);
  Int_t binx = data->GetVerticalAxis()->FindBin(y);

  hprofile->Reset();

  for (Int_t i=1; i<=hprofile->GetNbinsX(); ++i)
    {
      hprofile->SetBinContent(i, h3->GetBinContent(binx, biny, i));
      hprofile->SetBinError(i, h3->GetBinError(binx, biny, i));
    }

  constexpr double epsilon = 0.001;
  if (hprofile->Integral()<epsilon)
    return;

  // int n=2;
  // TF1 *f = nullptr;
  // std::string fname;
  // double chi2ndf = 0.0;
  // const double zmin = -130.0;
  // const double zmax = 230.0;

  // for (n=2; n<=9; ++n) {
  //   //    fname = "chebyshev" + std::to_string(n);
  //   fname = "pol" + std::to_string(n);
  //   hprofile->Fit(fname.data(), "", "", zmin, zmax);
  //   f = hprofile->GetFunction(fname.data());
  //   chi2ndf = f->GetChisquare()/f->GetNDF();
  //   if (chi2ndf<1.0)
  //     break;
  // }

  // const double maxfit = f->GetMaximum(zmin, zmax);
  // const double maxdata = histo->GetBinContent(biny, binx);

  // hprofile->SetTitle(Form("%s,%s=(%d,%d) #bullet %s #bullet #chi^{2}/ndf = %.1f #bullet max(fit) = %g #bullet max(fit)/max(data) = %g ;%s",
  // 			  data->GetVerticalAxis()->GetName(),data->GetHorizontalAxis()->GetName(),
  // 			  y, x, fname.data(), chi2ndf, maxfit, maxfit/maxdata,
  // 			  data->GetNormalAxis()->GetTitle()));

  hprofile->SetTitle("");
  hprofile->Draw("hist,e");
  // if (f)
  //   f->Draw("same");


  TAxis *yaxis = hprofile->GetYaxis();
  yaxis->SetMaxDigits(3);
  yaxis->SetTitle(histo->GetZaxis()->GetTitle());
  pad->SetLogy(logy);

  pad->Update();

  return;
}
