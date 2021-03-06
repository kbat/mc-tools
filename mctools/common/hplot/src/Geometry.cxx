#include "TColor.h"
#include "Geometry.h"

Geometry::Geometry(const std::string& fname, const std::string& hname,
		   const std::shared_ptr<Arguments> args) : Data(fname, hname, args)
{

}

void Geometry::SetH2(std::shared_ptr<TH2> h2)
{
  h2->SetLineWidth(args->GetMap()["glwidth"].as<size_t>());

  const Int_t col = TColor::GetColor(args->GetMap()["glcolor"].as<std::string>().c_str());
  h2->SetLineColor(col);

  h2->SetContour(args->GetMap()["gcont"].as<size_t>());

  const std::string opt = "same " + args->GetMap()["goption"].as<std::string>();
  h2->SetOption(opt.c_str());

  return;
}

Geometry::~Geometry()
{
}

std::shared_ptr<TH2> Geometry::Draw(const Float_t val) const
{
  std::shared_ptr <TH2> h2 = GetH2(val);
  h2->Draw(GetGOption().c_str());

  return h2;
}

void Geometry::BuildMaxH2()
{
  //  std::cout << "Geometry::BuildMaxH2" << std::endl;
  const Int_t n3x = h3->GetNbinsX();
  const Int_t n3y = h3->GetNbinsY();
  const Int_t n3z = h3->GetNbinsZ();

  std::string name = Form("%s_max", h3->GetName());
  std::string title = "max";
  h2max = MakeH2(name, title);

  if (plane == "xy")
    {
      const Int_t k = h3->GetZaxis()->FindBin(offset);
      for (Int_t j=1; j<=n3y; ++j)
	for (Int_t i=1; i<=n3x; ++i)
	  {
	    Double_t val = h3->GetBinContent(i,j,k);
	    h2max->SetBinContent(j,i,val);
	  }
    }
  else if (plane == "yx")
    {
      Int_t k = h3->GetZaxis()->FindBin(offset);
      for (Int_t j=1; j<=n3y; ++j)
	for (Int_t i=1; i<=n3x; ++i)
	  {
	    Double_t val = h3->GetBinContent(i,j,k);
	    h2max->SetBinContent(i,j,val);
	  }
    }
  else if (plane == "yz")
    {
      const Int_t i = h3->GetXaxis()->FindBin(offset);
      for (Int_t j=1; j<=n3y; ++j)
	for (Int_t k=1; k<=n3z; ++k)
	  {
	    Double_t val = h3->GetBinContent(i,j,k);
	    h2max->SetBinContent(k,j,val);
	  }
    }
  else if (plane == "zy")
    {
      const Int_t i = h3->GetXaxis()->FindBin(offset);
      for (Int_t j=1; j<=n3y; ++j)
	for (Int_t k=1; k<=n3z; ++k)
	  {
	    Double_t val = h3->GetBinContent(i,j,k);
	    h2max->SetBinContent(j,k,val);
	  }
    }
  else if (plane == "xz")
    {
      const Int_t j = h3->GetYaxis()->FindBin(offset);
      for (Int_t k=1; k<=n3z; ++k)
	for (Int_t i=1; i<=n3x; ++i)
	  {
	    Double_t val = h3->GetBinContent(i,j,k);
	    h2max->SetBinContent(k,i,val);
	  }
    }
  else if (plane == "zx")
    {
      const Int_t j = h3->GetYaxis()->FindBin(offset);
      for (Int_t k=1; k<=n3z; ++k)
	for (Int_t i=1; i<=n3x; ++i)
	  {
	    Double_t val = h3->GetBinContent(i,j,k);
	    h2max->SetBinContent(i,k,val);
	  }
    }

  SetH2(h2max);
}
