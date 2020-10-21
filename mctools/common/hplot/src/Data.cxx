#include <iostream>
#include <chrono>
#include <TFile.h>
#include "Data.h"

// Data::Data(const TH3* h3, const std::string& plane) :
//   h3(h3), h2(nullptr), plane(plane)
// {
//   // std::cout << "Data constructor" << std::endl;
//   // h3->Print();
// }

Data::Data(const std::string& fname, const std::string& hname,
	   const Arguments *args) :
  h3(nullptr), plane(""), args(args)
{
  plane = args->GetPlane();
  TFile df(fname.c_str());
  if (df.IsZombie()) {
    df.Close();
    exit(1);
  }
  TH3 *h3tmp(nullptr);
  df.GetObject<TH3>(hname.c_str(),h3tmp);
  if (!h3tmp) {
    std::cerr << "Error: Can't find " << hname << " in " << fname << std::endl;
    exit(1);
  }

  h3 = std::shared_ptr<TH3>(static_cast<TH3*>(h3tmp));
  h3->SetDirectory(0);
  df.Close();

  h3tmp = nullptr;

  h3->Scale(args->GetScale());
  offset = GetOffset(args->GetOffset());
}

void Data::SetH2(std::shared_ptr<TH2> h2)
{
  if (args->GetTitle() != "None")
    h2->SetTitle(args->GetTitle().c_str());
  else
    h2->SetTitle(Form("%s %s projection: %s", h3->GetTitle(), plane.c_str(), h2->GetTitle()));

  if (args->GetXTitle() != "None")
     h2->SetXTitle(args->GetXTitle().c_str());
  else
    h2->SetXTitle(GetHorizontalAxis()->GetTitle());

  if (args->GetYTitle() != "None")
    h2->SetYTitle(args->GetYTitle().c_str());
  else
    h2->SetYTitle(GetVerticalAxis()->GetTitle());

  if (args->GetZTitle() != "None")
    h2->SetZTitle(args->GetZTitle().c_str());

  h2->SetContour(args->GetMap()["dcont"].as<size_t>());
  h2->SetOption(args->GetDoption().c_str());

  const double zmin(args->GetZMin());
  if (zmin>std::numeric_limits<float>::lowest())
    h2->SetMinimum(zmin);

  const double zmax(args->GetZMax());
  if (zmax<std::numeric_limits<float>::max())
    h2->SetMaximum(zmax);

  return;
}

Data::~Data()
{

}

TAxis *Data::GetNormalAxis() const
{
  /*!
    Return the plane normal axis
   */

  if (plane.find("x")==std::string::npos)
    return h3->GetXaxis();
  else if (plane.find("y")==std::string::npos)
    return h3->GetYaxis();
  else if (plane.find("z")==std::string::npos)
    return h3->GetZaxis();
  else {
    std::cerr << "Error: wrong plane " << plane << std::endl;
    return nullptr;
  }
}

char Data::GetNormalAxisName() const
{
  /*!
    Return the plane normal axis
   */

  if (plane.find("x")==std::string::npos)
    return 'x';
  else if (plane.find("y")==std::string::npos)
    return 'y';
  else if (plane.find("z")==std::string::npos)
    return 'z';
  else {
    std::cerr << "Error: wrong plane " << plane << std::endl;
    return '?';
  }
}

TAxis *Data::GetHorizontalAxis() const
{
  if (plane[1] == 'x')
    return h3->GetXaxis();
  else if (plane[1] == 'y')
    return h3->GetYaxis();
  else if (plane[1] == 'z')
    return h3->GetZaxis();
  else
    {
      std::cerr << "Error in Data::GetHorizontalAxis()" << std::endl;
      return nullptr;
    }
}

TAxis *Data::GetVerticalAxis() const
{
  if (plane[0] == 'x')
    return h3->GetXaxis();
  else if (plane[0] == 'y')
    return h3->GetYaxis();
  else if (plane[0] == 'z')
    return h3->GetZaxis();
  else
    {
      std::cerr << "Error in Data::GetVerticalAxis()" << std::endl;
      return nullptr;
    }
}

void Data::Project()
{
  const Float_t xmin = GetVerticalAxis()->GetXmin();
  const Float_t xmax = GetVerticalAxis()->GetXmax();
  const Float_t ymin = GetHorizontalAxis()->GetXmin();
  const Float_t ymax = GetHorizontalAxis()->GetXmax();
  const Int_t nx = GetVerticalAxis()->GetNbins();
  const Int_t ny = GetHorizontalAxis()->GetNbins();

  const Int_t n3x = h3->GetNbinsX();
  const Int_t n3y = h3->GetNbinsY();
  const Int_t n3z = h3->GetNbinsZ();

  TAxis *a = GetNormalAxis();
  std::shared_ptr<TH2> h2(nullptr);

  for (Int_t bin=1; bin<=a->GetNbins(); ++bin)
    {
      const char *h2name = Form("%s_%d", h3->GetName(), bin);
      //      std::cout << "Data::Project: bin=" << bin << " " << h2name << std::endl;


      const char *h2title = Form("%g< %c < %g",
				 a->GetBinLowEdge(bin), GetNormalAxisName(), a->GetBinUpEdge(bin));

      if (h3->IsA() == TH3F::Class()) // data
	h2 = std::make_shared<TH2F>(h2name, h2title,     ny, ymin, ymax, nx, xmin, xmax);
      else if (h3->IsA() == TH3S::Class()) // geometry
	h2 = std::make_shared<TH2S>(h2name, h2title, ny, ymin, ymax, nx, xmin, xmax);
      else if (h3->IsA() == TH3I::Class()) // geometry
	h2 = std::make_shared<TH2I>(h2name, h2title, ny, ymin, ymax, nx, xmin, xmax);

      Float_t val, err;
      if (plane == "xy")
	{
	  for (Int_t i=1; i<=n3y; ++i)
	    for (Int_t j=1; j<=n3x; ++j) {
	      val = h3->GetBinContent(j,i,bin);
	      err = h3->GetBinError(j,i,bin);
	      h2->SetBinContent(i,j,val);
	      h2->SetBinError(i,j,err);
	    }
	}
      else if (plane == "yx")
	{
	  for (Int_t i=1; i<=n3y; ++i)
	    for (Int_t j=1; j<=n3x; ++j) {
	      val = h3->GetBinContent(j,i,bin);
	      err = h3->GetBinError(j,i,bin);
	      h2->SetBinContent(j,i,val);
	      h2->SetBinError(j,i,err);
	    }
	}
      else if (plane == "yz")
	{
	  std::cout << a->GetTitle() << std::endl;
	  for (Int_t i=1; i<=n3y; ++i)
	    for (Int_t j=1; j<=n3z; ++j) {
	      val = h3->GetBinContent(bin,i,j);
	      err = h3->GetBinError(bin,i,j);
	      h2->SetBinContent(j,i,val);
	      h2->SetBinError(j,i,err);
	    }
	}
      else if (plane == "zy")
	{
	  std::cout << a->GetTitle() << std::endl;
	  for (Int_t i=1; i<=n3y; ++i)
	    for (Int_t j=1; j<=n3z; ++j) {
	      val = h3->GetBinContent(bin,i,j);
	      err = h3->GetBinError(bin,i,j);
	      h2->SetBinContent(i,j,val);
	      h2->SetBinError(i,j,err);
	    }
	}
      else if (plane == "xz")
	{
	  std::cout << a->GetTitle() << std::endl;
	  for (Int_t i=1; i<=n3z; ++i)
	    for (Int_t j=1; j<=n3x; ++j) {
	      val = h3->GetBinContent(j,bin,i);
	      err = h3->GetBinError(j,bin,i);
	      h2->SetBinContent(i,j,val);
	      h2->SetBinError(i,j,err);
	    }
	}
      else if (plane == "zx")
	{
	  std::cout << a->GetTitle() << std::endl;
	  for (Int_t i=1; i<=n3z; ++i)
	    for (Int_t j=1; j<=n3x; ++j) {
	      val = h3->GetBinContent(j,bin,i);
	      err = h3->GetBinError(j,bin,i);
	      h2->SetBinContent(j,i,val);
	      h2->SetBinError(j,i,err);
	    }
	}

      SetH2(h2);

      vh2.push_back(h2);
    }

  return;
}

Float_t Data::GetOffset(const std::string& val) const
{
  float v(0.0);
  try {
    v = std::stof(val);
  }
  catch (std::invalid_argument const &e) {
    if (val != "centre")
      std::cerr << "GetOffset: unknown val value: " << val << std::endl;

    TAxis *a = GetNormalAxis();
    v = (a->GetXmax()+a->GetXmin())/2.0;
  }
  return v;
}

std::shared_ptr<TH2> Data::GetH2(const std::string val) const
{
  return GetH2(GetOffset(val));
}

std::shared_ptr<TH2> Data::GetH2(const Float_t val) const
{
  TAxis *a = GetNormalAxis();
  Int_t bin = a->FindBin(val);
  std::cerr << "bin: " << bin << "\t val: " << val << std::endl;

  if (bin>a->GetNbins())
    std::cerr << "Data::GetH2: bin>a->GetNbins() why?" << std::endl;
  else if (bin==0) {
    std::cerr << "Data:GetH2: bin = 0! why?" << std::endl;
    bin = 1;
  }

  return vh2[bin-1];
}

Bool_t Data::Check(TAxis *normal) const
{
  /*!
    Checks if data and geometry histograms can be used together
   */
  Bool_t val = kTRUE;
  const TAxis *myA = GetNormalAxis();

  if (myA->GetNbins() != normal->GetNbins())
    {
      std::cerr << "Data::Check(): geometry/data normal axes nbins are different:" << std::endl;
      std::cerr << "\t" << myA->GetNbins() << " " << normal->GetNbins() << std::endl;
      val = kFALSE;
    }

  if (std::abs(myA->GetXmin()-normal->GetXmin())>std::numeric_limits<double>::epsilon())
    {
      std::cerr << "Data::Check(): geometry/data normal axes have different min values:" << std::endl;
      std::cerr << "\t" << myA->GetXmin() << " " << normal->GetXmin() << std::endl;
      val = kFALSE;
    }

  if (std::abs(myA->GetXmax()-normal->GetXmax())>std::numeric_limits<double>::epsilon())
    {
      std::cerr << "Data::Check(): geometry/data normal axes have different max values:" << std::endl;
      std::cerr << "\t" << myA->GetXmax() << " " << normal->GetXmax() << std::endl;
      val = kFALSE;
    }

  return val;
}
