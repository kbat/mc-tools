h3(TCanvas *c1, TH3 *h, const int bin)
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
  TH3F *h1 = h->Clone(newname); // clone h into h1 to avoid overwiting previous histograms
  
  cout << h->GetName() << " has "  << h->GetNbinsZ() << " bins along the z-axis" << endl;
  const float zmin = h->GetZaxis()->GetBinLowEdge(bin);
  const float zmax = h->GetZaxis()->GetBinLowEdge(bin+1);
  cout << "\t bin #" << bin << " is between " << zmin
       << " and " << zmax << " cm" << endl;

  h1->GetZaxis()->SetRange(bin,bin);
  TH2 *h2 = h1->Project3D("xy");
  h2->SetTitle(Form("%s: bin %d (%g < z < %g)", h2->GetName(), bin, zmin, zmax));
  h2->Draw("colz"); // only for the selected z-bin
  gPad->SetLogz();

  c1->cd(4);
  // draw 2 histograms on the same pad
  TH1 *h4tot = h->ProjectionX(Form("%s_x",h->GetName())); // integrated over all y and z
  h4tot->SetLineColor(kBlack);
  h4tot->SetLineWidth(2);
  h4tot->SetTitle("total");
  TH1 *h4cut = h2->ProjectionX(Form("%s_x",h2->GetName())); // integrated over all y but only for selected z-bin
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

exfixed()
{
  gStyle->SetOptStat(kFALSE);
  gStyle->SetPadRightMargin(0.12); // shifts frame to allocate space for the z-axis in TH2
  
  TFile *f = new TFile("exfixed.root");
  f->ls();

  TCanvas *c1 = new TCanvas;
  c1->Print("c1.pdf[");
  
  h3(c1, piFluBin, 40);
  c1->Print("c1.pdf");
  c1->Clear();

  h3(c1, Edeposit, 3);
  c1->Print("c1.pdf");

  c1->Print("c1.pdf]");
}
