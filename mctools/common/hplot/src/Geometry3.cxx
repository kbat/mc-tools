#include "TColor.h"
#include "Geometry3.h"

Geometry3::Geometry3(const std::string& fname, const std::string& hname,
		   const std::shared_ptr<Arguments> args) :
  Geometry(fname, hname, args), Data3(fname, hname, args)
{

}

void Geometry3::SetH2(std::shared_ptr<TH2> h2)
{
  h2->SetLineWidth(args->GetMap()["glwidth"].as<size_t>());

  const Int_t col = TColor::GetColor(args->GetMap()["glcolor"].as<std::string>().data());
  h2->SetLineColorAlpha(col, args->GetMap()["glalpha"].as<float>());

  h2->SetContour(args->GetMap()["gcont"].as<size_t>());

  const std::string opt = "same " + args->GetMap()["goption"].as<std::string>();
  h2->SetOption(opt.data());

  return;
}

Geometry3::~Geometry3()
{
}

std::shared_ptr<TH2> Geometry3::Draw(const Float_t val) const
{
  std::shared_ptr <TH2> h2 = GetH2(val);
  h2->Draw(GetGOption().data());

  return h2;
}

void Geometry3::BuildMaxH2()
{
  //  std::cout << "Geometry3::BuildMaxH2" << std::endl;
  const Int_t n3x = h3->GetNbinsX();
  const Int_t n3y = h3->GetNbinsY();
  const Int_t n3z = h3->GetNbinsZ();

  std::string name = Form("%s_max", h3->GetName());
  std::string title = "max";
  h2max = MakeH2(name, title);

  const TAxis *zAxis = h3->GetZaxis();
  Float_t ofs = offset;
  const Double_t zmin = zAxis->GetBinLowEdge(1);
  const Double_t zmax = zAxis->GetBinUpEdge(zAxis->GetLast());

  if ((ofs<zmin) || (ofs>=zmax)) {
    ofs = (std::abs(ofs-zmin) < std::abs(ofs-zmax)) ? GetOffset("min") : GetOffset("max");
    if (args->IsVerbose()) {
      std::cout << "Info: Setting geometry offset to " << ofs <<
	" because the original value (" << offset << ") is outside the geometry histogram range. ";
      std::cout << "Override it with the -offset option." << std::endl;
    }
  }

  if (plane == "xy")
    {
      const Int_t k = zAxis->FindBin(ofs);
      for (Int_t j=1; j<=n3y; ++j)
	for (Int_t i=1; i<=n3x; ++i)
	  {
	    Double_t val = h3->GetBinContent(i,j,k);
	    h2max->SetBinContent(j,i,val);
	  }
    }
  else if (plane == "yx")
    {
      Int_t k = zAxis->FindBin(ofs);
      for (Int_t j=1; j<=n3y; ++j)
	for (Int_t i=1; i<=n3x; ++i)
	  {
	    Double_t val = h3->GetBinContent(i,j,k);
	    h2max->SetBinContent(i,j,val);
	  }
    }
  else if (plane == "yz")
    {
      const Int_t i = h3->GetXaxis()->FindBin(ofs);
      for (Int_t j=1; j<=n3y; ++j)
	for (Int_t k=1; k<=n3z; ++k)
	  {
	    Double_t val = h3->GetBinContent(i,j,k);
	    h2max->SetBinContent(k,j,val);
	  }
    }
  else if (plane == "zy")
    {
      const Int_t i = h3->GetXaxis()->FindBin(ofs);
      for (Int_t j=1; j<=n3y; ++j)
	for (Int_t k=1; k<=n3z; ++k)
	  {
	    Double_t val = h3->GetBinContent(i,j,k);
	    h2max->SetBinContent(j,k,val);
	  }
    }
  else if (plane == "xz")
    {
      const Int_t j = h3->GetYaxis()->FindBin(ofs);
      for (Int_t k=1; k<=n3z; ++k)
	for (Int_t i=1; i<=n3x; ++i)
	  {
	    Double_t val = h3->GetBinContent(i,j,k);
	    h2max->SetBinContent(k,i,val);
	  }
    }
  else if (plane == "zx")
    {
      const Int_t j = h3->GetYaxis()->FindBin(ofs);
      for (Int_t k=1; k<=n3z; ++k)
	for (Int_t i=1; i<=n3x; ++i)
	  {
	    Double_t val = h3->GetBinContent(i,j,k);
	    h2max->SetBinContent(i,k,val);
	  }
    }

  SetH2(h2max);
}
