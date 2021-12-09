example(const char *fname="wssa.root")
{
  /*
    Some VERY simple examples to do analysis of SSW files with ROOT.
    See $ROOTSYS/tutorials for more information
   */

  TFile *f = new TFile(fname);
  T->Print();

  // The tree contains numbers from the SSW file, but it is possible to build several more convenient variables.
  // See the lines with SetAlias in ssw2root.py
  // Let's print the list of these new variables:
  T->GetListOfAliases()->Print();

  TCanvas *c = new TCanvas;
  c->Divide(3,2);

  // plot particle IDs we have in the SSW file
  // Note: use "IPT" instead of "particle" with MCNPX
  c->cd(1);
  T->Draw("particle", "weight");
  gPad->SetLogy();

  c->cd(2); // energy spectrum of neutrons
  T->Draw("energy", "weight*(surface==1426 && particle==1)");
  gPad->SetLogy();

  c->cd(2); // energy spectrum of neutrons crossing the give surface
  T->Draw("energy", "weight*(surface==1426 && particle==1)");
  gPad->SetLogy();

  c->cd(3); // same but plot log energy and set number of bins and lower/upper x-axis limits
  T->Draw("log10(energy)>>h(100, -10, 2)", "weight*(surface==1426 && particle==1)");
  gPad->SetLogy();
  gPad->SetGrid();

  c->cd(4); // log energy vs time in msec
  T->Draw("log10(energy):time/1E+5", "weight*(surface==1426 && particle==1)", "colz");
  gPad->SetLogz();

  c->cd(5); // you can rotate this plot with mouse
  T->Draw("x:y:z", "weight*(surface!=1426)", "");

  c->cd(6); // use first 1E+6 hits only and set arbitrary title
  // note that 1E+6 refers to the number of records in the SSW file (tracks crossed your surfaces), not to the number of incident particles
  T->Draw("y:theta", "weight*(surface==1426 && particle==1)", "colz", 1E+6);
  T->GetHistogram()->SetTitle("title;xtitle;ytitle");
}
