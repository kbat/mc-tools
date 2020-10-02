#include <iostream>
#include <TROOT.h>
#include <TColor.h>
#include <TStyle.h>
#include <TApplication.h>
#include <TCanvas.h>
#include <TFile.h>
#include <TH3F.h>
#include <TH1.h>
//#include <TRint.h>
#include "Arguments.h"
#include "MainFrame.h"

void SetColourMap()
{
  /*!
    Sets the colour map used at MAX IV
  */

  // PView is exported from ParaView
  const std::vector<Float_t> PView{0, 0.27843137254900002, 0.27843137254900002, 0.85882352941200002,
				   0.143, 0, 0, 0.36078431372500003,
				   0.285, 0, 1, 1,
				   0.429, 0, 0.50196078431400004, 0,
				   0.571, 1, 1, 0,
				   0.714, 1, 0.38039215686299999, 0,
				   0.857, 0.419607843137, 0, 0,
				   1, 0.87843137254899994, 0.30196078431399997, 0.30196078431399997};

  constexpr UInt_t NColors = 99;
  constexpr UInt_t NRGBs = 8;

  std::vector<Double_t> stops, red, green, blue;

  for (UInt_t i=0; i<NRGBs; ++i) {
    stops.push_back(PView[4*i]);
    red.push_back(PView[4*i]+1);
    green.push_back(PView[4*i]+2);
    blue.push_back(PView[4*i]+3);
  }

  TColor::CreateGradientColorTable(NRGBs, &stops[0], &red[0], &green[0], &blue[0], NColors);

  return;
}


int main(int argc, const char **argv)
{

  Arguments args(argc, argv);

  if (args.IsHelp())
    return 0;

  if (!args.test())
    return 1;

  const po::variables_map vm = args.GetMap();

  //  gROOT->SetBatch(true);
  gStyle->SetOptStat(kFALSE);

  const size_t width = vm["width"].as<size_t>();
  size_t height = vm["height"].as<size_t>();
  if (height==0)
    height = int(width*2.0/(1.0+sqrt(5.0))); // golden ratio

  const char *dfname = vm["dfile"].as<std::string>().c_str();
  TFile *df = new TFile(dfname);
  if (df->IsZombie())
    return 1;
  df->ls();

  const char *dhname = vm["dhist"].as<std::string>().c_str();
  TH3F *h3 = nullptr;
  df->GetObject<TH3F>(dhname,h3);


  TApplication theApp("App",&argc,const_cast<char**>(argv));

  MainFrame *mf = new MainFrame(gClient->GetRoot(), 800, 600);
  mf->SetWindowName(args.GetTitle().c_str());
  SetColourMap();

  TCanvas *c1 = mf->GetCanvas();
  if (args.IsSlice())
    c1->Divide(1,2);

  c1->cd(1);
  int nthreads = 4;
  ROOT::EnableImplicitMT(nthreads);

  TH1 *h2 = h3->Project3D(args.GetPlane().c_str());
  h2->Draw("colz");

  theApp.Run();

  //  delete mf;

  return 0;
}
