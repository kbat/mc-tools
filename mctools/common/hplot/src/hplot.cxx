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
#include <TColor.h>
#include "Arguments.h"
#include "MainFrame.h"
#include "Data3.h"
#include "Geometry.h"

void SetColourMap(const std::string& palette="MAXIV")
{
  /*!
    Set the colour map scheme
  */
  std::string pal(palette);
  bool invert(false);

  if (pal.front() == '-')
    {
      pal.erase(0,1);
      invert = true;
    }

  if (pal == "MAXIV")
    {
      // This is actually very close to Rainbow palette
      // (almost the same as saying gStyle->SetPalette(kRainBow))
      // Disadvantages of kRainBow are discussed here: https://root.cern/blog/rainbow-color-map

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
    }
  else
    { // https://root.cern.ch/doc/master/classTColor.html
      // tail -23 core/base/inc/TColor.h|sed -e "s;\(k[a-z][A-Z]*\);\{\"\1\"=\1;gi" -e "s;\=[0-9].;};g"
      std::map<std::string, EColorPalette> p { {"kDeepSea", kDeepSea},            {"kGreyScale", kGreyScale},  {"kDarkBodyRadiator", kDarkBodyRadiator},
					       {"kBlueYellow", kBlueYellow},      {"kRainBow", kRainBow},      {"kInvertedDarkBodyRadiator", kInvertedDarkBodyRadiator},
					       {"kBird", kBird},                  {"kCubehelix", kCubehelix},  {"kGreenRedViolet", kGreenRedViolet},
					       {"kBlueRedYellow", kBlueRedYellow},{"kOcean", kOcean},          {"kColorPrintableOnGrey", kColorPrintableOnGrey},
					       {"kAlpine", kAlpine},              {"kAquamarine", kAquamarine},{"kArmy", kArmy},
					       {"kAtlantic", kAtlantic},          {"kAurora", kAurora},        {"kAvocado", kAvocado},
					       {"kBeach", kBeach},                {"kBlackBody", kBlackBody},  {"kBlueGreenYellow", kBlueGreenYellow},
					       {"kBrownCyan", kBrownCyan},        {"kCMYK", kCMYK},            {"kCandy", kCandy},
					       {"kCherry", kCherry},              {"kCoffee", kCoffee},        {"kDarkRainBow", kDarkRainBow},
					       {"kDarkTerrain", kDarkTerrain},    {"kFall", kFall},            {"kFruitPunch", kFruitPunch},
					       {"kFuchsia", kFuchsia},            {"kGreyYellow", kGreyYellow},{"kGreenBrownTerrain", kGreenBrownTerrain},
					       {"kGreenPink", kGreenPink},        {"kIsland", kIsland},        {"kLake", kLake},
					       {"kLightTemperature", kLightTemperature}, {"kLightTerrain", kLightTerrain}, {"kMint", kMint},
					       {"kNeon", kNeon},                  {"kPastel", kPastel},        {"kPearl", kPearl},
					       {"kPigeon", kPigeon},              {"kPlum", kPlum},            {"kRedBlue", kRedBlue},
					       {"kRose", kRose},                  {"kRust", kRust},            {"kSandyTerrain", kSandyTerrain},
					       {"kSienna", kSienna},              {"kSolar", kSolar},          {"kSouthWest", kSouthWest},
					       {"kStarryNight", kStarryNight},    {"kSunset", kSunset},        {"kTemperatureMap", kTemperatureMap},
					       {"kThermometer", kThermometer},    {"kValentine", kValentine},  {"kVisibleSpectrum", kVisibleSpectrum},
					       {"kWaterMelon", kWaterMelon},      {"kCool", kCool},            {"kCopper", kCopper},
					       {"kGistEarth", kGistEarth},        {"kViridis", kViridis},      {"kCividis", kCividis} };
      const EColorPalette &val = p[pal];
      if (val != 0)
	gStyle->SetPalette(val);
      else
	std::cout << "hplot warning: palette " << palette << " not known." << std::endl;
    }

  if (invert)
    TColor::InvertPalette();

  return;
}


int main(int argc, const char **argv)
{
  std::shared_ptr<Arguments> args = std::make_shared<Arguments>(argc, argv);

  if (args->IsHelp())
    return 0;

  if (!args->test())
    return 1;

  const po::variables_map vm = args->GetMap();

  gStyle->SetOptStat(kFALSE);
  SetColourMap(args->GetPalette());

  std::string dfname = vm["dfile"].as<std::string>();
  std::string dhname = vm["dhist"].as<std::string>();
  std::string gfname = vm["gfile"].as<std::string>();
  std::string ghname = vm["ghist"].as<std::string>();

  std::shared_ptr<Data3> data = std::make_shared<Data3>(dfname, dhname, args);
  auto start = std::chrono::high_resolution_clock::now();
  data->Project();
  data->PrintChrono(start, "Data3::Project: ");

  std::shared_ptr<Geometry> geo(nullptr);
  if (!gfname.empty())
    {
      geo = std::make_shared<Geometry>(gfname, ghname, args);
      auto start = std::chrono::high_resolution_clock::now();
      geo->Project();
      geo->PrintChrono(start,"Geometry::Project: ");
      data->Check(geo->GetNormalAxis());
    }

  std::unique_ptr<MainFrame>   mf(nullptr);
  // These must be raw pointers due to ROOT garbage collectors:
  TCanvas                     *c1(nullptr);
  TApplication            *theApp(nullptr);

  UInt_t width = args->GetWidth();
  UInt_t height = args->GetHeight();

  if (args->IsBatch())
    {
      c1 = new TCanvas("hplot", args->GetWindowTitle().data(), width, height);
    }
  else
    {
      theApp = new TApplication("hplot", &argc, const_cast<char**>(argv), nullptr, -1);

      mf = std::make_unique<MainFrame>(gClient->GetRoot(), width, height, data, geo);
      mf->SetWindowName(args->GetWindowTitle().data());

      c1 = dynamic_cast<TCanvas*>(mf->GetCanvas());

      // Int_t x, y;
      // gVirtualX->GetWindowSize(gClient->GetRoot()->GetId(), x, y, width, height);
    }

  TVirtualPad *h2pad  = c1;

  if ((args->IsSlice()) && (!args->IsBatch())) {
    c1->Divide(1,2);
    c1->cd(1);
    h2pad = c1->GetPad(1);
  }

  if (args->IsZTitle())
      c1->SetRightMargin(vm["right_margin"].as<float>());

  data->Draw();

  h2pad->SetLogz(args->IsLogz() && !args->IsErrors());

  if (geo)
      geo->Draw();

  if (args->IsBatch())
    {
      const Int_t oldLevel = gErrorIgnoreLevel;
      gErrorIgnoreLevel = kWarning; // suppress the "Info in <TCanvas::Print>" message
      c1->Print(vm["o"].as<std::string>().data());
      gErrorIgnoreLevel = oldLevel;
      delete c1; c1 = nullptr;
    }
  else
    {
      theApp->Run(kTRUE);
    }

  //gObjectTable->Print();

  return 0;
}
