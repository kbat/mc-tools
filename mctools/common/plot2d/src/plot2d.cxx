#include <iostream>
#include <chrono>

#include <TROOT.h>
#include <TColor.h>
#include <TStyle.h>
#include <TApplication.h>
#include <TCanvas.h>
#include <TFile.h>
#include <TH3F.h>
#include <TH1.h>
#include <TObjectTable.h>
#include <TMath.h>
#include <TVirtualX.h>
//#include <TRint.h>
#include "Arguments.h"
#include "MainFrame.h"
#include "Data.h"

void RebinToScreen(std::shared_ptr<TH2F> h2)
{
  std::clog << "RebinToScreen" << std::endl;

  const Int_t nx = h2->GetNbinsX();
  const Int_t ny = h2->GetNbinsY();

  Int_t x, y;
  UInt_t w, h;
  gVirtualX->GetWindowSize(gClient->GetRoot()->GetId(), x, y, w, h);
  //  std::cout << x << " " << y << std::endl;
  std::cout << " screen size: " << w << " " << h << std::endl;

  std::cout << " h2 before: " << h2->GetNbinsX() << " " << h2->GetNbinsY() << std::endl;

  const Int_t scaleX =
    TMath::Ceil(h2->GetNbinsX()/static_cast<float>(w));
  if (scaleX>=2)
    h2->RebinX(scaleX);
  const Int_t scaleY =
    TMath::Ceil(h2->GetNbinsY()/static_cast<float>(h));
  if (scaleY>=2)
    h2->RebinY(scaleY);

  std::cout << "h2 after: " << h2->GetNbinsX() << " " << h2->GetNbinsY() << std::endl;
  return;
}

void SetColourMap()
{
  /*!
    Sets the colour map used at MAX IV
  */

  // PView is exported from ParaView
  const std::vector<Float_t>
    PView{0, 0.27843137254900002, 0.27843137254900002, 0.85882352941200002,
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

  std::string dfname = vm["dfile"].as<std::string>();

  std::string dhname = vm["dhist"].as<std::string>();
  Data data(dfname, dhname, &args);

  const std::shared_ptr<TH3F> h3 = data.GetH3();
  const std::shared_ptr<TH2F> h2 = data.GetH2();

  std::cout << "h2 bins: " << h2->GetNbinsX() << " " << h2->GetNbinsY() << std::endl;

  TApplication theApp("App",&argc,const_cast<char**>(argv));

  MainFrame *mf = new MainFrame(gClient->GetRoot(), args.GetWidth(), args.GetHeight());
  mf->SetWindowName(args.GetWindowTitle().c_str());
  SetColourMap();


  TCanvas *c1 = mf->GetCanvas();
  if (args.GetZTitle() != "None")
    c1->SetRightMargin(args.GetMap()["right_margin"].as<float>());


  RebinToScreen(h2);

  h2->Draw("colz"); // 3 sec to draw

  //    gObjectTable->Print();

  theApp.Run();

  //  delete mf;


  return 0;
}

// Performance:
// h2  - Project3D + draw = 8 sec (same time with Python script)
//   since it takes 8 sec to draw -> 5 sec to Project3D
// h2 - Data::Project + draw = 5 sec (since it takes 3 sec to draw -> 2 sec to project)
// project and draw both = 13 sec -> correct
