void h3(TCanvas *c1, TH3 *h, const int bin)
{
  c1->Divide(2,2);

  c1->cd(1);
  h->Project3D("xy")->Draw("colz"); // integrated over all z
  gPad->SetLogz();

  c1->cd(2);
  h->Project3D("xz")->Draw("colz"); // integrated over all y
  gPad->SetLogz();

  c1->cd(3);
  // Object names should be unique in ROOT. That's why we use the 'newname' variable.
  // In a simple script it can be omitted.
  const char *newname = Form("%s_cloned",h->GetName());
  const auto h1 = dynamic_cast<TH3F*>(h->Clone(newname)); // clone h into h1 to avoid overwiting previous histograms

  cout << h->GetName() << " has "  << h->GetNbinsZ() << " bins along the z-axis" << endl;
  const float zmin = h->GetZaxis()->GetBinLowEdge(bin);
  const float zmax = h->GetZaxis()->GetBinUpEdge(bin);
  cout << "\t bin #" << bin << " is between " << zmin
       << " and " << zmax << " cm" << endl;

  h1->GetZaxis()->SetRange(bin,bin);


  const auto h2 = dynamic_cast<TH2*>(h1->Project3D("xy"));
  h2->SetTitle(Form("%s: bin %d (%g < z < %g)", h2->GetName(), bin, zmin, zmax));
  h2->Draw("colz"); // only for the selected z-bin
  gPad->SetLogz();

  // Drawing 2 histograms on the same pad:
  c1->cd(4);
  const auto h4tot = h->ProjectionX(Form("%s_x",h->GetName())); // integrated over all y and z
  h4tot->SetLineColor(kBlack);
  h4tot->SetLineWidth(2);
  h4tot->SetTitle("total");

  // h4cut is integrated over all y but only for the selected z-bin
  const auto h4cut = h2->ProjectionX(Form("%s_x",h2->GetName()));
  h4cut->SetLineColor(kRed);
  h4cut->SetTitle("selected z-bin");

  THStack *hs = new THStack("hs", ";x [cm]");
  hs->Add(h4tot);
  hs->Add(h4cut);
  hs->Draw("hist,e,nostack");
  gPad->SetGrid();
  gPad->SetLogy();

  TLegend *leg = new TLegend(0.7, 0.85, 0.99, 0.99);
  leg->AddEntry(h4tot, h4tot->GetTitle(), "l");
  leg->AddEntry(h4cut, h4cut->GetTitle(), "l");
  leg->Draw();
}

void exfixed()
{
  gStyle->SetOptStat(kFALSE);
  gStyle->SetPadRightMargin(0.12); // shifts frame to allocate space for the z-axis in TH2

  const auto f = TFile::Open("exfixed.root");
  //  f->ls();
  const auto piFluBin = f->Get<TH3F>("piFluBin");
  const auto Edeposit = f->Get<TH3F>("Edeposit");
  const auto pi3 = f->Get<TH1F>("piFluenU");
  pi3->SetLineColor(kRed);
  pi3->SetLineWidth(3);
  const auto pi4 = f->Get<TH1F>("piFluenD");
  pi4->SetLineWidth(3);

  const auto c1 = new TCanvas;
  c1->Print("c1.pdf[");

  h3(c1, piFluBin, 40);
  c1->Print("c1.pdf");
  c1->Clear();

  h3(c1, Edeposit, 3);
  c1->Print("c1.pdf");

  const auto c2 = new TCanvas("c2", "Fluence spectra");
  const auto hs = new THStack("hs", "Charged pion fluence;Energy [GeV];Fluence [1/GeV/cm^{2}]");
  hs->Add(pi3);
  hs->Add(pi4);
  hs->Draw("nostack hist e");
  hs->GetXaxis()->SetTitleOffset(1.2);

  const auto leg = new TLegend(0.3, 0.35, 0.65, 0.49);
  leg->AddEntry(pi3, pi3->GetTitle(), "l");
  leg->AddEntry(pi4, pi4->GetTitle(), "l");
  leg->Draw();

  gPad->SetLogx();
  gPad->SetLogy();
  gPad->SetGrid();

  c2->Print("c1.pdf");

  c1->Print("c1.pdf]");
}
