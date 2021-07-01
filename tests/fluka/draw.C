void plot2D(TFile *f, const char *hname, const Float_t x=0.0)
{
  //  gPad->SetRightMargin(0.12);
  const auto h3 = f->Get<TH3F>(hname);
  const auto axis = h3->GetXaxis();
  const Int_t bin = axis->FindBin(x);
  axis->SetRange(bin,bin);

  const auto h2 = h3->Project3D("yz");
  h2->Draw("colz");
  gPad->SetLogz();
}

void plot1D(TFile *f, const char *hname1, const char *hname2=0)
{
  const auto hs = new THStack("hs", "");

  const auto h1 = f->Get<TH2F>(hname1);
  const auto h1x = h1->ProjectionX();
  hs->Add(h1x);

  if (hname2) {
    const auto h2 = f->Get<TH2F>(hname2);
    const auto h2x = h2->ProjectionX();
    h2x->SetLineColor(kRed);
    hs->Add(h2x);
  }
  hs->Draw("hist,e,nostack");
  hs->SetMinimum(1e-6);
  hs->GetXaxis()->SetTitle(h1x->GetXaxis()->GetTitle());
  hs->GetYaxis()->SetTitle(h1x->GetYaxis()->GetTitle());
  hs->SetTitle(h1x->GetTitle());
}

void draw(const char *fname="test.root")
{
  gStyle->SetOptStat(1);
  // const Int_t current(500); // mA
  // // single charged particles per second
  // const Double_t persec(current/1000.0/TMath::Qe());

  TFile *f = new TFile(fname);

  TCanvas *c1 = new TCanvas;
  c1->Divide(4,2);

  c1->cd(1);
  plot2D(f, "piFluBin");

  c1->cd(2);
  plot2D(f, "Edeposit");

  c1->cd(3);
  plot1D(f, "pFluenUD", "pFluenUD_lowneu");
  gPad->SetLogx();
  gPad->SetLogy();

  c1->cd(4);
  plot1D(f, "piCurrUD");
  gPad->SetLogx();
  gPad->SetLogy();

  c1->cd(5);
  auto resnuc = f->Get<TH2F>("resnuc");
  resnuc->Draw("colz");

  c1->cd(6);
  auto resnucA = f->Get<TGraphErrors>("resnucA");
  resnucA->Draw("AP");

  c1->cd(7);
  auto resnucZ = f->Get<TGraphErrors>("resnucZ");
  resnucZ->Draw("AP");

  c1->Print("draw.pdf");
}
