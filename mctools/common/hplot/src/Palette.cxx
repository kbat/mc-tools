#include <iostream>
#include <map>
#include <vector>

#include <TColor.h>
#include <TStyle.h>

#include "Palette.h"

namespace {

  /*!
    The MAX IV palette, exported from ParaView.

    This is actually very close to the Rainbow palette (almost the same as
    saying gStyle->SetPalette(kRainBow)).  The disadvantages of kRainBow are
    discussed here: https://root.cern/blog/rainbow-color-map
  */
  void SetMAXIV()
  {
    const std::vector<Float_t>
      PView{0,     0.27843137254900002, 0.27843137254900002, 0.85882352941200002,
	    0.143, 0,                   0,                   0.36078431372500003,
	    0.285, 0,                   1,                   1,
	    0.429, 0,                   0.50196078431400004, 0,
	    0.571, 1,                   1,                   0,
	    0.714, 1,                   0.38039215686299999, 0,
	    0.857, 0.419607843137,      0,                   0,
	    1,     0.87843137254899994, 0.30196078431399997, 0.30196078431399997};

    constexpr UInt_t NColors = 99;
    constexpr UInt_t NRGBs = 8;

    std::vector<Double_t> stops, red, green, blue;

    for (UInt_t i=0; i<NRGBs; ++i) {
      stops.push_back(PView[4*i]);
      red.push_back(PView[4*i+1]);
      green.push_back(PView[4*i+2]);
      blue.push_back(PView[4*i+3]);
    }

    TColor::CreateGradientColorTable(NRGBs, stops.data(), red.data(),
				     green.data(), blue.data(), NColors);
    gStyle->SetNumberContours(NColors);
  }

  /*!
    The palettes predefined by ROOT.
    https://root.cern.ch/doc/master/classTColor.html

    tail -23 core/base/inc/TColor.h | \
      sed -e "s;\(k[a-z][A-Z]*\);\{\"\1\"=\1;gi" -e "s;\=[0-9].;};g"
  */
  const std::map<std::string, EColorPalette>& ROOTPalettes()
  {
    static const std::map<std::string, EColorPalette> p {
      {"kDeepSea", kDeepSea},                   {"kGreyScale", kGreyScale},
      {"kDarkBodyRadiator", kDarkBodyRadiator}, {"kBlueYellow", kBlueYellow},
      {"kRainBow", kRainBow},                   {"kBird", kBird},
      {"kInvertedDarkBodyRadiator", kInvertedDarkBodyRadiator},
      {"kCubehelix", kCubehelix},               {"kGreenRedViolet", kGreenRedViolet},
      {"kBlueRedYellow", kBlueRedYellow},       {"kOcean", kOcean},
      {"kColorPrintableOnGrey", kColorPrintableOnGrey},
      {"kAlpine", kAlpine},                     {"kAquamarine", kAquamarine},
      {"kArmy", kArmy},                         {"kAtlantic", kAtlantic},
      {"kAurora", kAurora},                     {"kAvocado", kAvocado},
      {"kBeach", kBeach},                       {"kBlackBody", kBlackBody},
      {"kBlueGreenYellow", kBlueGreenYellow},   {"kBrownCyan", kBrownCyan},
      {"kCMYK", kCMYK},                         {"kCandy", kCandy},
      {"kCherry", kCherry},                     {"kCoffee", kCoffee},
      {"kDarkRainBow", kDarkRainBow},           {"kDarkTerrain", kDarkTerrain},
      {"kFall", kFall},                         {"kFruitPunch", kFruitPunch},
      {"kFuchsia", kFuchsia},                   {"kGreyYellow", kGreyYellow},
      {"kGreenBrownTerrain", kGreenBrownTerrain}, {"kGreenPink", kGreenPink},
      {"kIsland", kIsland},                     {"kLake", kLake},
      {"kLightTemperature", kLightTemperature}, {"kLightTerrain", kLightTerrain},
      {"kMint", kMint},                         {"kNeon", kNeon},
      {"kPastel", kPastel},                     {"kPearl", kPearl},
      {"kPigeon", kPigeon},                     {"kPlum", kPlum},
      {"kRedBlue", kRedBlue},                   {"kRose", kRose},
      {"kRust", kRust},                         {"kSandyTerrain", kSandyTerrain},
      {"kSienna", kSienna},                     {"kSolar", kSolar},
      {"kSouthWest", kSouthWest},               {"kStarryNight", kStarryNight},
      {"kSunset", kSunset},                     {"kTemperatureMap", kTemperatureMap},
      {"kThermometer", kThermometer},           {"kValentine", kValentine},
      {"kVisibleSpectrum", kVisibleSpectrum},   {"kWaterMelon", kWaterMelon},
      {"kCool", kCool},                         {"kCopper", kCopper},
      {"kGistEarth", kGistEarth},               {"kViridis", kViridis},
      {"kCividis", kCividis}
    };

    return p;
  }

}

bool SetColourMap(const std::string& palette)
{
  std::string pal(palette);
  bool invert(false);

  if (!pal.empty() && (pal.front() == '-'))
    {
      pal.erase(0,1);
      invert = true;
    }

  if (pal == "MAXIV")
    {
      SetMAXIV();
    }
  else
    {
      const auto& known = ROOTPalettes();
      const auto it = known.find(pal);
      if (it == known.end())
	{
	  std::cerr << "hplot warning: palette " << palette << " not known." << std::endl;
	  return false;
	}
      gStyle->SetPalette(it->second);
    }

  if (invert)
    TColor::InvertPalette();

  return true;
}
