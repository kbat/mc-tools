void plot2D(TFile *f, const char *hname, const Float_t x=0.0)
{
  //  gPad->SetRightMargin(0.12);
  TH3F *h3 = dynamic_cast<TH3F*>(f->Get(hname));
  TAxis *axis = h3->GetXaxis();
  const Int_t bin = axis->FindBin(x);
  axis->SetRange(bin,bin);

  TH1* h2 = h3->Project3D("yz");
  h2->Draw("colz");
  gPad->SetLogz();
}

void plot1D(TFile *f, const char *hname1, const char *hname2=0)
{
  THStack *hs = new THStack("hs", "");

  TH2F *h1 = dynamic_cast<TH2F*>(f->Get(hname1));
  TH1D *h1x = h1->ProjectionX();
  hs->Add(h1x);
  //h1x->Draw("hist,e");

  if (hname2) {
      TH2F *h2 = dynamic_cast<TH2F*>(f->Get(hname2));
      TH1D *h2x = h2->ProjectionX();
      h2x->SetLineColor(kRed);
      h2x->Draw("hist,e,same");
      hs->Add(h2x);
    }
  hs->Draw("hist,e,nostack");
  hs->SetMinimum(1e-6);
}

void draw(const char *fname="shield.root")
{
  gStyle->SetOptStat(0);
  const Int_t current(500); // mA
  // single charged particles per second
  const Double_t persec(current/1000.0/TMath::Qe());

  TFile *f = new TFile(fname);

  TCanvas *c1 = new TCanvas;
  c1->Divide(4,2);

  c1->cd(1);
  plot2D(f, "meshH");

  c1->cd(2);
  plot2D(f, "meshP");

  c1->cd(3);
  plot2D(f, "meshE");

  c1->cd(4);
  plot2D(f, "meshN");

  c1->cd(5);
  plot1D(f, "eFwd", "eBack");
  gPad->SetLogy();

  c1->cd(6);
  plot1D(f, "pFwd", "pBack");
  gPad->SetLogy();
}
