#include <array>
#include <cmath>
#include <iostream>

#include "TColor.h"
#include "Geometry3.h"

Geometry3::Geometry3(TH3 *h3, const std::shared_ptr<Arguments> args) :
  Data3(h3, args), drawn(nullptr)
{
}

void Geometry3::SetH2(std::shared_ptr<TH2> h2) const
{
  h2->SetLineWidth(args->GetGlwidth());

  const Int_t col = TColor::GetColor(args->GetGlcolor().data());
  h2->SetLineColorAlpha(col, args->GetGlalpha());

  h2->SetContour(args->GetGcont());

  const std::string opt = "same " + args->GetGoption();
  h2->SetOption(opt.data());

  return;
}

void Geometry3::Draw(Float_t offset)
{
  drawn = GetH2(offset);
  drawn->Draw(GetGOption().data());
}

std::string Geometry3::StatusText(Double_t x, Double_t y) const
{
  const std::shared_ptr<TH2> h2 = drawn ? drawn : GetH2(Data3::GetOffset());
  if (!h2)
    return "";

  const Int_t binx = h2->GetXaxis()->FindFixBin(x);
  const Int_t biny = h2->GetYaxis()->FindFixBin(y);

  return Form("Material: %d", static_cast<int>(h2->GetBinContent(binx, biny)));
}

void Geometry3::BuildMaxH2()
{
  /*!
    The geometry has no "max" - with the -max option the data histogram loses
    its normal axis, so the geometry is simply shown at the requested offset,
    which gives a representative view.
  */
  std::string name = Form("%s_max", h3->GetName());
  std::string title = "max";
  h2max = MakeH2(name, title);

  const TAxis *na = GetNormalAxis();
  Float_t ofs = offset;
  const Double_t nmin = na->GetBinLowEdge(1);
  const Double_t nmax = na->GetBinUpEdge(na->GetLast());

  if ((ofs<nmin) || (ofs>=nmax)) {
    ofs = (std::abs(ofs-nmin) < std::abs(ofs-nmax)) ? GetOffset("min") : GetOffset("max");
    if (args->IsVerbose()) {
      std::cout << "Info: Setting geometry offset to " << ofs <<
	" because the original value (" << offset << ") is outside the geometry histogram range. ";
      std::cout << "Override it with the -offset option." << std::endl;
    }
  }

  const Int_t n = na->FindBin(ofs);
  const Int_t nv = GetVerticalAxis()->GetNbins();
  const Int_t nh = GetHorizontalAxis()->GetNbins();

  for (Int_t v=1; v<=nv; ++v)
    for (Int_t h=1; h<=nh; ++h)
      {
	const std::array<Int_t,3> b = plane.Bin3(v, h, n);
	h2max->SetBinContent(h, v, h3->GetBinContent(b[0], b[1], b[2]));
      }

  SetH2(h2max);
}
