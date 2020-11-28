#include <iostream>
#include <TMath.h>
#include <TFile.h>
#include <TGaxis.h>
#include <TCanvas.h>
#include "Data.h"

// Data::Data(const TH3* h3, const std::string& plane) :
//   h3(h3), h2(nullptr), plane(plane)
// {
//   // std::cout << "Data constructor" << std::endl;
//   // h3->Print();
// }

Data::Data(const std::string& fname, const std::string& hname,
	   const Arguments *args) :
  h3(nullptr), plane(""), yrev(nullptr), h2max(nullptr), args(args)
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

  if (args->IsRebin())
    {
      auto start = std::chrono::high_resolution_clock::now();
      Rebin();
      PrintChrono(start, " "+GetTypeStr()+": Rebin");
    }

  if (args->IsFlipped())
    {
      auto start = std::chrono::high_resolution_clock::now();
      Flip();
      PrintChrono(start, " "+GetTypeStr()+"::Flip: ");
    }

  h3tmp = nullptr;

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

  // TODO: better to define TH2 taking into account [xy]min/max than
  // limiting the axes
  if (args->IsXmin())
    h2->GetXaxis()->SetRangeUser(args->GetXmin(), args->GetXmax());

  TAxis *a = h2->GetYaxis();
  if (args->IsYmin()) {
    if (args->IsFlipped()) {
      const float xmin = a->GetXmin();
      const float xmax = a->GetXmax();
      const float dy = args->GetYmax()-args->GetYmin();
      const float dmax = xmax-args->GetYmax();

      a->SetRangeUser(xmin+dmax, xmin+dmax+dy);
      //      std::cout << a->GetBinLowEdge(a->GetFirst()) << " "
      // << a->GetBinUpEdge(a->GetLast()) << std::endl;
    }
    else
      a->SetRangeUser(args->GetYmin(), args->GetYmax());
   }
    //  std::cout << a->GetXmin() << " " << a->GetXmax() << std::endl;
    //  std::cout << a->GetBinLowEdge(a->GetFirst()) << " "
    // << a->GetBinUpEdge(a->GetLast()) << std::endl;
  return;
}

void Data::Flip()
{
  /*!
    Flip the h3 along the TH2 vertical axis
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

void Data::Rebin() const
{
  /*!
    Rebin the histogram so that it is not larger than width x height
   */

  const Int_t width = args->GetWidth();
  const Int_t height = args->GetHeight();

  const Int_t nx = GetHorizontalAxis()->GetNbins();
  const Int_t ny = GetVerticalAxis()->GetNbins();

  const Int_t scaleX =
    TMath::Ceil(nx/static_cast<float>(width));
  if (scaleX==0)
    {
      std::cerr << "hplot: ERROR: scaleX = 0" << std::endl;
      exit(1);
    }

  const Int_t scaleY =
    TMath::Ceil(ny/static_cast<float>(height));
  if (scaleY==0)
    {
      std::cerr << "hplot: ERROR: scaleY = 0" << std::endl;
      exit(1);
    }

  if ((scaleX>=2) || (scaleY>=2)) {
    if (plane == "xy")
      h3->Rebin3D(scaleY, scaleX, 1);
    else if (plane == "yx")
      h3->Rebin3D(scaleX, scaleY, 1);
    else if (plane == "yz")
      h3->Rebin3D(1, scaleY, scaleX);
    else if (plane == "zy")
      h3->Rebin3D(1, scaleX, scaleY);
    else if (plane == "xz")
      h3->Rebin3D(scaleY, 1, scaleX);
    else if (plane == "zx")
      h3->Rebin3D(scaleX, 1, scaleY);

    if (GetType() == kData) // we do not need to scale geometry
      {
	auto start = std::chrono::high_resolution_clock::now();
	h3->Scale(1.0/(scaleX*scaleY));
	PrintChrono(start, " Rebin: "+GetTypeStr() + " scale after rebin: ");
      }
  }

  if (args->IsVerbose())
    {
      std::cout << "Rebinning " << h3->GetName() << ": before: " << nx << " x " << ny;
      std::cout << "\t after: " << GetHorizontalAxis()->GetNbins() << " x " << GetVerticalAxis()->GetNbins();
      std::cout << "\t by factor " << scaleX << " x " << scaleY << std::endl;
    }
  return;
}

void Data::BuildMaxH2()
/*!
  Build the histogram with max values along the normal axis
  (called if the -max argument is used)
 */
{
  const std::shared_ptr<TH2> h2 = vh2[0];
  h2max = std::shared_ptr<TH2>(dynamic_cast<TH2*>(h2->Clone("hmax")));
  //  h2max->Reset();

  const Int_t nx = h2->GetNbinsX();
  const Int_t ny = h2->GetNbinsY();

  for (Int_t i=1; i<=nx; ++i)
    for (Int_t j=1; j<ny; ++j)
      {
	Double_t max = 0.0;
	Double_t err = 0.0;
	for (const auto h : vh2)
	  {
	    Float_t val = h->GetBinContent(i,j);
	    if (max<val)
	      {
		max = val;
		err = h->GetBinError(i,j);
	      }
	  }
	if (max>0.0)
	  {
	    h2max->SetBinContent(i,j,max);
	    h2max->SetBinError(i,j,err);
	  }
      }
}

void Data::ReverseYAxis(std::shared_ptr<TH2> h) const
{
  TAxis *ay = h->GetYaxis();

  double ymin = ay->GetBinLowEdge(ay->GetFirst());
  double ymax = ay->GetBinUpEdge(ay->GetLast());

  if (args->IsYmin())
    {
      // TODO: not exactly correct
      // will cause problems with rought binning
      ymin = args->GetYmin();
      ymax = args->GetYmax();
    }

  // Remove the current axis
  ay->SetLabelOffset(999);
  ay->SetTickLength(0);

  // Redraw the new axis
  gPad->Update();
  if (!yrev)
    {
      yrev = std::make_shared<TGaxis>(gPad->GetUxmin(),
      				      gPad->GetUymax(),
      				      gPad->GetUxmin()-0.001,
      				      gPad->GetUymin(),
      				      ymin,ymax,
      				      510,"+");
      yrev->SetLabelOffset(-0.03);
      yrev->SetLabelFont(ay->GetLabelFont());
      yrev->SetLabelSize(ay->GetLabelSize());
      yrev->SetLabelColor(ay->GetLabelColor());
    }
  yrev->Draw();
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
  if (GetType() == kData) // we do not need to scale geometry
    {
      auto start = std::chrono::high_resolution_clock::now();
      h3->Scale(args->GetScale());
      PrintChrono(start, " Project: "+GetTypeStr() + " scale ");
    }

  const TAxis *va = GetVerticalAxis();
  const TAxis *ha = GetHorizontalAxis();
  const TAxis *na = GetNormalAxis();

  const Float_t xmin = va->GetXmin();
  const Float_t xmax = va->GetXmax();
  const Float_t ymin = ha->GetXmin();
  const Float_t ymax = ha->GetXmax();

  const Int_t nx = va->GetNbins();
  const Int_t ny = ha->GetNbins();

  const Int_t n3x = h3->GetNbinsX();
  const Int_t n3y = h3->GetNbinsY();
  const Int_t n3z = h3->GetNbinsZ();

  const Int_t nbins = na->GetNbins();
  vh2.reserve(nbins);

  std::shared_ptr<TH2> h2(nullptr);

  for (Int_t bin=1; bin<=nbins; ++bin)
    {
      const char *h2name = Form("%s_%d", h3->GetName(), bin);
       const char *h2title = Form("%g< %c < %g",
				 na->GetBinLowEdge(bin), GetNormalAxisName(), na->GetBinUpEdge(bin));

      if (h3->IsA() == TH3F::Class()) // data
	h2 = std::make_shared<TH2F>(h2name, h2title,     ny, ymin, ymax, nx, xmin, xmax);
      else if (h3->IsA() == TH3S::Class()) // geometry
	h2 = std::make_shared<TH2S>(h2name, h2title, ny, ymin, ymax, nx, xmin, xmax);
      else if (h3->IsA() == TH3I::Class()) // geometry
	h2 = std::make_shared<TH2I>(h2name, h2title, ny, ymin, ymax, nx, xmin, xmax);
      else {
	std::cerr << "ERROR: unknown TH3 class name, " << h3->ClassName() << std::endl;
	exit(1);
      }

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
	  //	  std::cout << na->GetTitle() << std::endl;
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
	  //	  std::cout << na->GetTitle() << std::endl;
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
	  //	  std::cout << na->GetTitle() << std::endl;
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
	  //	  std::cout << na->GetTitle() << std::endl;
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

      // TAxis *a = h2->GetYaxis();
      // float xmin = a->GetBinLowEdge(a->GetFirst());
      // float xmax = a->GetBinUpEdge(a->GetLast());
      // std::cout << xmin << " " << xmax << " " << nbins << " " << a->GetNbins() << std::endl;

      // if (args->IsFlipped()) // reverse vertical axis
      // 	{
      // 	  TAxis *a = h2->GetYaxis();
      // 	  const float xmin = a->GetBinLowEdge(a->GetFirst());
      // 	  const float xmax = a->GetBinUpEdge(a->GetLast());
      // 	  const int nbins = a->GetLast()-a->GetFirst()+1;
      // 	  a->Set(nbins, -xmax, -xmin);
      // 	}

      vh2.push_back(h2);
    }

  if (args->IsMax())
    BuildMaxH2();

  return;
}

Float_t Data::GetOffset(const std::string& val) const
{
  float v(0.0);
  try {
    v = std::stof(val);
  }
  catch (std::invalid_argument const &e) {
    TAxis *a = GetNormalAxis();
    if (val == "centre")
      {
	v = (a->GetXmax()+a->GetXmin())/2.0;
      }
    else if (val == "min")
      {
	v = a->GetBinCenter(1);
      }
    else if (val == "max")
      {
	v = a->GetBinCenter(a->GetLast());
      }
    else
      std::cerr << "Data::GetOffset(): unknown argument: " << val << std::endl;
  }

  return v;
}

std::shared_ptr<TH2> Data::GetH2(const std::string val) const
{
  if (val.empty())
    return GetH2(GetOffset(args->GetOffset()));
  else
    return GetH2(GetOffset(val));
}

std::shared_ptr<TH2> Data::GetH2(const Float_t val) const
{
  if (h2max)
    return h2max;
  else
    {
      const TAxis *a = GetNormalAxis();
      const Int_t nbins = a->GetNbins();
      Int_t bin = a->FindBin(val);

      if (bin>nbins) {
	std::cerr << "Data::GetH2: bin>a->GetNbins() why?" << std::endl;
	bin = nbins;
      } else if (bin==0) {
	std::cerr << "Data:GetH2: bin = 0! why?" << std::endl;
	bin = 1;
      }

      return vh2[bin-1];
    }
}

std::shared_ptr<TH2> Data::Draw(const Float_t val) const
/*!
  Draws h2 at the given offset
 */
{
  std::shared_ptr <TH2> h2 = GetH2(val);

  h2->Draw();

  if (args->IsFlipped())
    ReverseYAxis(h2);

  return h2;
}

std::shared_ptr<TH2> Data::Draw(const std::string val) const
/*!
  Draws h2 at the given offset
 */
{
  if (val.empty())
    return Draw(GetOffset(args->GetOffset()));
  else
    return Draw(GetOffset(val));
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

void Data::PrintChrono(std::chrono::system_clock::time_point start, std::string msg) const
{
  if (args->IsVerbose())
    {
      auto delta = std::chrono::high_resolution_clock::now()-start;
      std::cout << msg << ": " << std::chrono::duration_cast<std::chrono::milliseconds>(delta).count() << " ms" << std::endl;
    }
}
