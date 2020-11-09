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

  //  auto start = std::chrono::high_resolution_clock::now();
  if (args->IsFlipped())
    Flip();
  // auto delta = std::chrono::high_resolution_clock::now()-start;
  // std::cout << " Data::Flip: " << std::chrono::duration_cast<std::chrono::milliseconds>(delta).count() << " ms" << std::endl;

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

  if (args->IsZmin())
    h2->SetMinimum(args->GetZmin());

  if (args->IsZmax())
    h2->SetMaximum(args->GetZmax());

  return;
}

void Data::Flip()
{
  /*!
    Flip the h3 along the Y axis
  */
  const std::string hname(Form("%s_%s", h3->GetName(), "flipped"));
  std::shared_ptr<TH3> flipped = std::shared_ptr<TH3>(static_cast<TH3*>(h3->Clone(hname.c_str())));
  flipped->Reset();

  const Int_t nx = h3->GetNbinsX();
  const Int_t ny = h3->GetNbinsY();
  const Int_t nz = h3->GetNbinsZ();

  if (plane[0]=='x') // vertical axis is 'x'
    {
      for (Int_t i=1; i<=nx; ++i)
	for (Int_t j=1; j<=ny; ++j)
	  for (Int_t k=1; k<=nz; ++k)
	    {
	      const Double_t val = h3->GetBinContent(i,j,k);
	      const Double_t err = h3->GetBinError(i,j,k);
	      const Int_t ii(nx+1-i);
	      flipped->SetBinContent(ii, j, k, val);
	      flipped->SetBinError(ii,   j, k, err);
	    }
    }
  else if (plane[0]=='y') // vertical axis is 'y'
    {
      for (Int_t i=1; i<=nx; ++i)
	for (Int_t j=1; j<=ny; ++j)
	  for (Int_t k=1; k<=nz; ++k)
	    {
	      const Double_t val = h3->GetBinContent(i,j,k);
	      const Double_t err = h3->GetBinError(i,j,k);
	      const Int_t jj(ny+1-j);
	      flipped->SetBinContent(i, jj, k, val);
	      flipped->SetBinError(i,   jj, k, err);
	    }
    }
  else if (plane[0]=='z') // vertical axis is 'z'
    {
      for (Int_t i=1; i<=nx; ++i)
	for (Int_t j=1; j<=ny; ++j)
	  for (Int_t k=1; k<=nz; ++k)
	    {
	      const Double_t val = h3->GetBinContent(i,j,k);
	      const Double_t err = h3->GetBinError(i,j,k);
	      const Int_t kk(nz+1-k);
	      flipped->SetBinContent(i, j, kk, val);
	      flipped->SetBinError(i,   j, kk, err);
	    }
    }
  h3 = std::move(flipped);

  return;
}

void Data::ErrorHist(std::shared_ptr<TH2> h) const
/*!
  Replace values with their relative errors
 */
{
  const Int_t nx = h->GetNbinsX();
  const Int_t ny = h->GetNbinsY();
  for (Int_t i=1; i<=nx; ++i)
    for (Int_t j=1; j<=ny; ++j)
      {
	const Double_t val = h->GetBinContent(i,j);
	Double_t err = std::abs(val)>0.0 ?
	  100.0 * h->GetBinError(i,j) / val : 0.0;
	h->SetBinContent(i,j,err);
	h->SetBinError(i,j,0.0);
	if (err>100.0)
	  std::cout << "Warning: relative error > 100%:\t" << err << std::endl;
      }

  h->GetZaxis()->SetTitle("Relative error [%]");

  Float_t zmin(args->GetZmin());
  Float_t zmax(args->GetZmax());

  if (zmax>100.0)
    zmax = 100.0;
  h->SetMaximum(zmax);

  if (!args->IsZmin()) {
    //	zmin = h->GetBinContent(h2->GetMinimumBin());
    zmin = h->GetMinimum(0.0); // return min bin content > 0.0
    h->SetMinimum(zmin);
  }

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
  const Int_t nbins = a->GetNbins();
  vh2.reserve(nbins);
  std::shared_ptr<TH2> h2(nullptr);

  for (Int_t bin=1; bin<=nbins; ++bin)
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

      if (args->IsErrors())
	ErrorHist(h2);

      if (args->IsFlipped()) // reverse vertical axis
	{
	  TAxis *a = h2->GetYaxis();
	  a->Set(a->GetNbins(), -a->GetXmax(), -a->GetXmin());
	}

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
