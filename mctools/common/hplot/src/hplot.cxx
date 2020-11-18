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
#include "Arguments.h"
#include "MainFrame.h"
#include "Data.h"
#include "Geometry.h"

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
    red.push_back(PView[4*i+1]);
    green.push_back(PView[4*i+2]);
    blue.push_back(PView[4*i+3]);
  }

  TColor::CreateGradientColorTable(NRGBs, stops.data(), red.data(), green.data(), blue.data(), NColors);
  gStyle->SetNumberContours(NColors);

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

  gStyle->SetOptStat(kFALSE);
  SetColourMap();

  std::string dfname = vm["dfile"].as<std::string>();
  std::string dhname = vm["dhist"].as<std::string>();
  std::string gfname = vm["gfile"].as<std::string>();
  std::string ghname = vm["ghist"].as<std::string>();

  std::shared_ptr<Data> data = std::make_shared<Data>(dfname, dhname, &args);
  auto start = std::chrono::high_resolution_clock::now();
  data->Project();
  data->PrintChrono(start, "Data::Project: ");

  std::shared_ptr<Geometry> geo(nullptr);
  if (!gfname.empty())
    {
      geo = std::make_shared<Geometry>(gfname, ghname, &args);
      auto start = std::chrono::high_resolution_clock::now();
      geo->Project();
      geo->PrintChrono(start,"Geometry::Project: ");
      data->Check(geo->GetNormalAxis());
    }

  // These must be raw pointers due to ROOT garbage collectors:
  TCanvas      *c1(nullptr);
  MainFrame    *mf(nullptr);
  TApplication *theApp(nullptr);

  UInt_t width = args.GetWidth();
  UInt_t height = args.GetHeight();

  if (args.IsBatch())
    {
      c1 = new TCanvas("hplot", args.GetWindowTitle().c_str(), width, height);
    }
  else
    {
      theApp = new TApplication("hplot", &argc, const_cast<char**>(argv), nullptr, -1);

      mf = new MainFrame(gClient->GetRoot(), width, height, data, geo);
      mf->SetWindowName(args.GetWindowTitle().c_str());

      c1 = mf->GetCanvas();

      // Int_t x, y;
      // gVirtualX->GetWindowSize(gClient->GetRoot()->GetId(), x, y, width, height);
    }

  if ( args->IsZTitle() )
      c1->SetRightMargin(vm["right_margin"].as<float>());

  data->Draw();

  c1->SetLogz(args.IsLogz() && !args.IsErrors());

  // GEOMETRY

  if (geo)
      geo->Draw();

  if (args.IsBatch())
    {
      c1->Print(vm["o"].as<std::string>().c_str());
      delete c1; c1 = nullptr;
    }
  else
    {
      theApp->Run(kTRUE);
    }

  delete mf; mf = nullptr;

  //gObjectTable->Print();

  return 0;
}

// Performance:
// h2  - Project3D + draw = 8 sec (same time with Python script)
//   since it takes 8 sec to draw -> 5 sec to Project3D
// h2 - Data::Project + draw = 5 sec (since it takes 3 sec to draw -> 2 sec to project)
// project and draw both = 13 sec -> correct
