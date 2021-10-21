#include <iostream>
#include <TMath.h>
#include <TFile.h>
#include <TGaxis.h>
#include <TCanvas.h>
#include "Data3.h"

Data3::Data3(const std::string& fname, const std::string& hname,
	     const std::shared_ptr<Arguments> args) :
  Data(fname,hname,args),
  yrev(nullptr), plane(""), h3(nullptr), h2max(nullptr)
{
  plane = args->GetPlane();
  TFile df(fname.data());
  if (df.IsZombie()) {
    df.Close();
    exit(1);
  }
  TH3 *h3tmp(nullptr);
  df.GetObject<TH3>(hname.data(),h3tmp);
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

void Data3::SetH2(std::shared_ptr<TH2> h2)
{
  if (args->GetTitle() != "None")
    h2->SetTitle(args->GetTitle().data());
  else
    h2->SetTitle(Form("%s %s projection: %s", h3->GetTitle(), plane.data(), h2->GetTitle()));

  if (args->GetXTitle() != "None")
     h2->SetXTitle(args->GetXTitle().data());
  else
    h2->SetXTitle(GetHorizontalAxis()->GetTitle());

  if (args->GetYTitle() != "None")
    h2->SetYTitle(args->GetYTitle().data());
  else
    h2->SetYTitle(GetVerticalAxis()->GetTitle());

  if (args->GetZTitle() != "None")
    h2->SetZTitle(args->GetZTitle().data());

  h2->SetContour(args->GetMap()["dcont"].as<size_t>());
  h2->SetOption(args->GetDoption().data());

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

void Data3::Flip()
{
  /*!
    Flip the h3 along the TH2 vertical axis
  */
  const std::string hname(Form("%s_%s", h3->GetName(), "flipped"));
  std::shared_ptr<TH3> flipped = std::shared_ptr<TH3>(static_cast<TH3*>(h3->Clone(hname.data())));
  flipped->Reset();

  const Int_t nx = h3->GetNbinsX();
  const Int_t ny = h3->GetNbinsY();
  const Int_t nz = h3->GetNbinsZ();

  Int_t i, j, k, ii;

  auto f = [&](Int_t& i, Int_t& j, Int_t& k,
	       Int_t n, const Int_t& m, Int_t& q,
	       const Int_t& a, const Int_t& b, const Int_t& c)
	   {
	     for (i=1; i<=nx; ++i)
	       for (j=1; j<=ny; ++j)
		 for (k=1; k<=nz; ++k)
		   {
		     const Double_t val = h3->GetBinContent(i,j,k);
		     const Double_t err = h3->GetBinError(i,j,k);
		     q = n+1-m;
		     flipped->SetBinContent(a, b, c, val);
		     flipped->SetBinError(a,   b, c, err);
		   }
	   };

  if (plane[0]=='x')
    f(i,j,k,nx,i,ii,ii,j,k);
  if (plane[0]=='y')
    f(i,j,k,ny,j,ii,i,ii,k);
  if (plane[0]=='z')
    f(i,j,k,nz,k,ii,i,j,ii);

  h3 = std::move(flipped);

  return;
}

void Data3::ErrorHist(std::shared_ptr<TH2> h) const
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
	if (err>101.0)
	  std::cout << "Warning: relative error > 101%:\t" << err << std::endl;
      }

  h->GetZaxis()->SetTitle("Relative error [%]");

  Float_t zmin(args->GetZmin());
  Float_t zmax(args->GetZmax());

  if (zmax>100.0)
    zmax = 100.0;
  h->SetMaximum(zmax);

  if (!args->IsZmin()) {
    //	zmin = h->GetBinContent(h2->GetMinimumBin());
    zmin = 0.0; //h->GetMinimum(0.0); // return min bin content > 0.0
    h->SetMinimum(zmin);
  }

  return;
}

void Data3::Rebin() const
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

    if (GetType() == kData3) // we do not need to scale geometry
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

void Data3::BuildMaxH2()
{
  //  std::cout << "Data3::BuildMaxH2" << std::endl;
  const Int_t n3x = h3->GetNbinsX();
  const Int_t n3y = h3->GetNbinsY();
  const Int_t n3z = h3->GetNbinsZ();

  std::string name = Form("%s_max", h3->GetName());
  std::string title = "max";
  h2max = MakeH2(name, title);

  Int_t i,j,k;

  auto f = [&](Int_t &i,  Int_t &j,  Int_t &k,
	       Int_t NI,  Int_t NJ,  Int_t NK,
	       Int_t &ii, Int_t &jj, Int_t &kk,
	       Int_t &x,  Int_t&y)
	   {
	     for (j=1; j<=NJ; ++j)
	       for (i=1; i<=NI; ++i)
		 {

		   Double_t max(0.0);
		   Double_t err(0.0);
		   for (k=1; k<=NK; ++k)
		     {
		       const Double_t val = h3->GetBinContent(ii,jj,kk);
		       const Double_t e = h3->GetBinError(ii,jj,kk);
		       //		       if ((args->IsMaxErr(val,e)) && (max<val)) {
		       if ((args->IsMaxErr(val,e)) && (max+err<val-e)) {
			 max = val;
			 err = e;
		       }
		     }
		   if (max>0.0)
		     {
		       h2max->SetBinContent(x,y,max);
		       h2max->SetBinError(x,y,err);
		     }
		 }
	   };


  if (plane == "xy")
    f(j,i,k,n3y,n3x,n3z,i,j,k,j,i);
  else if (plane == "yx")
    f(j,i,k,n3y,n3x,n3z,i,j,k,i,j);
  else if (plane == "yz")
    f(j,k,i,n3y,n3z,n3x,i,j,k,k,j);
  else if (plane == "zy")
    f(j,k,i,n3y,n3z,n3x,i,j,k,j,k);
  else if (plane == "xz")
    f(k,i,j,n3z,n3x,n3y,i,j,k,k,i);
  else if (plane == "zx")
    f(k,i,j,n3z,n3x,n3y,i,j,k,i,k);

  SetH2(h2max);
  if (args->IsErrors())
    ErrorHist(h2max);

  return;
}

void Data3::ReverseYAxis(std::shared_ptr<TH2> h) const
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


Data3::~Data3()
{

}

TAxis *Data3::GetNormalAxis() const
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

char Data3::GetNormalAxisName() const
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

TAxis *Data3::GetHorizontalAxis() const
{
  if (plane[1] == 'x')
    return h3->GetXaxis();
  else if (plane[1] == 'y')
    return h3->GetYaxis();
  else if (plane[1] == 'z')
    return h3->GetZaxis();
  else
    {
      std::cerr << "Error in Data3::GetHorizontalAxis()" << std::endl;
      return nullptr;
    }
}

TAxis *Data3::GetVerticalAxis() const
{
  if (plane[0] == 'x')
    return h3->GetXaxis();
  else if (plane[0] == 'y')
    return h3->GetYaxis();
  else if (plane[0] == 'z')
    return h3->GetZaxis();
  else
    {
      std::cerr << "Error in Data3::GetVerticalAxis()" << std::endl;
      return nullptr;
    }
}

std::shared_ptr<TH2> Data3::MakeH2(std::string& name, std::string& title)
/*!
  Create the TH2 histogram from based on the projection plane and TH3 binning
 */
{
  const TAxis *va = GetVerticalAxis();
  const TAxis *ha = GetHorizontalAxis();

  const Float_t xmin = va->GetXmin();
  const Float_t xmax = va->GetXmax();
  const Float_t ymin = ha->GetXmin();
  const Float_t ymax = ha->GetXmax();

  const Int_t nx = va->GetNbins();
  const Int_t ny = ha->GetNbins();

  std::shared_ptr<TH2> h2(nullptr);

  if (h3->IsA() == TH3F::Class())      // data
    h2 = std::make_shared<TH2F>(name.data(), title.data(), ny, ymin, ymax, nx, xmin, xmax);
  else if (h3->IsA() == TH3D::Class()) // also data
    h2 = std::make_shared<TH2D>(name.data(), title.data(), ny, ymin, ymax, nx, xmin, xmax);
  else if (h3->IsA() == TH3S::Class()) // geometry
    h2 = std::make_shared<TH2S>(name.data(), title.data(), ny, ymin, ymax, nx, xmin, xmax);
  else if (h3->IsA() == TH3I::Class()) // also geometry
    h2 = std::make_shared<TH2I>(name.data(), title.data(), ny, ymin, ymax, nx, xmin, xmax);
  else {
    std::cerr << "ERROR: unknown TH3 class name, " << h3->ClassName() << std::endl;
    exit(1);
  }

  return h2;
}


void Data3::Project()
{
  if (GetType() == kData3) // we do not need to scale geometry
    {
      auto start = std::chrono::high_resolution_clock::now();
      h3->Scale(args->GetScale());
      PrintChrono(start, " Project: "+GetTypeStr() + " scale ");
    }

  if (args->IsMax())
    {
      BuildMaxH2();
      return;
    }
  else
    {
      const TAxis *na = GetNormalAxis();
      const Int_t nbins = na->GetNbins();
      vh2.reserve(nbins);

      const Int_t n3x = h3->GetNbinsX();
      const Int_t n3y = h3->GetNbinsY();
      const Int_t n3z = h3->GetNbinsZ();

      std::shared_ptr<TH2> h2(nullptr);

      Int_t  i,j;
      auto f = [&](Int_t &i,  Int_t &j,
		   Int_t NI,  Int_t NJ,
		   Int_t &xx, Int_t &yy, Int_t &kk,
		   Int_t &x,  Int_t &y)
	       {
		 for (i=1; i<=NI; ++i)
		   for (j=1; j<=NJ; ++j) {
		     const Double_t val = h3->GetBinContent(xx,yy,kk);
		     const Double_t err = h3->GetBinError(xx,yy,kk);
		     if (args->IsMaxErr(val,err)) {
		       h2->SetBinContent(x,y,val);
		       h2->SetBinError(x,y,err);
		     }
		   }
	       };

      for (Int_t bin=1; bin<=nbins; ++bin)
	{
	  std::string h2name  = Form("%s_%d", h3->GetName(), bin);
	  std::string h2title = Form("%g< %c < %g",
				     na->GetBinLowEdge(bin), GetNormalAxisName(),
				     na->GetBinUpEdge(bin));

	  h2 = MakeH2(h2name, h2title);

	  if (plane == "xy")
	    f(i,j,n3y,n3x,j,i,bin,i,j);
	  else if (plane == "yx")
	    f(i,j,n3y,n3x,j,i,bin,j,i);
	  else if (plane == "yz")
	    f(i,j,n3y,n3z,bin,i,j,j,i);
	  else if (plane == "zy")
	    f(i,j,n3y,n3z,bin,i,j,i,j);
	  else if (plane == "xz")
	    f(i,j,n3z,n3x,j,bin,i,i,j);
	  else if (plane == "zx")
	    f(i,j,n3z,n3x,j,bin,i,j,i);

	  SetH2(h2);

	  if (args->IsErrors())
	    ErrorHist(h2);

	  vh2.push_back(h2);
	}
    }

  return;
}

Float_t Data3::GetOffset(const std::string& val) const
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
      std::cerr << "Data3::GetOffset(): unknown argument: " << val << std::endl;
  }

  return v;
}

std::shared_ptr<TH2> Data3::GetH2(const std::string val) const
{
  if (val.empty())
    return GetH2(GetOffset(args->GetOffset()));
  else
    return GetH2(GetOffset(val));
}

std::shared_ptr<TH2> Data3::GetH2(const Float_t val) const
{
  if (h2max)
    return h2max;
  else
    {
      const TAxis *a = GetNormalAxis();
      const Int_t nbins = a->GetNbins();
      Int_t bin = a->FindBin(val);

      if (bin>nbins) {
	std::cerr << "Data3::GetH2: bin>a->GetNbins() why? " << bin << " " << nbins << std::endl;
	bin = nbins;
      } else if (bin==0) {
	std::cerr << "Data3:GetH2: bin = 0! why?" << std::endl;
	bin = 1;
      }

      return vh2[bin-1];
    }
}

std::shared_ptr<TH2> Data3::Draw(const Float_t val) const
/*!
  Draws h2 at the given offset
 */
{
  std::shared_ptr <TH2> h2 = GetH2(val);

  h2->Draw();

  if (args->IsFlipped())
    ReverseYAxis(h2);

  if (args->IsVerbose())
    {
      Int_t locmix, locmax, locmiy, locmay, locmiz, locmaz;
      std::cout << "min: " << h2->GetBinContent(h2->GetMinimumBin(locmix,locmiy,locmiz)) << " at (" << h2->GetXaxis()->GetBinCenter(locmix) << ", " << h2->GetYaxis()->GetBinCenter(locmiy) << ")\t" << std::flush;
      std::cout << "max: " << h2->GetBinContent(h2->GetMaximumBin(locmax,locmay,locmaz)) << " at (" << h2->GetXaxis()->GetBinCenter(locmax) << ", " << h2->GetYaxis()->GetBinCenter(locmay) << ")" << std::endl;
    }

  return h2;
}

std::shared_ptr<TH2> Data3::Draw(const std::string val) const
/*!
  Draws h2 at the given offset
 */
{
  if (val.empty())
    return Draw(GetOffset(args->GetOffset()));
  else
    return Draw(GetOffset(val));
}

Bool_t Data3::Check(TAxis *normal) const
{
  /*!
    Checks if data and geometry histograms can be used together
   */
  Bool_t val = kTRUE;
  const TAxis *myA = GetNormalAxis();

  if (myA->GetNbins() != normal->GetNbins())
    {
      std::cerr << "Data3::Check(): geometry/data normal axes nbins are different:" << std::endl;
      std::cerr << "\t" << myA->GetNbins() << " " << normal->GetNbins() << std::endl;
      val = kFALSE;
    }

  if (std::abs(myA->GetXmin()-normal->GetXmin())>std::numeric_limits<double>::epsilon())
    {
      std::cerr << "Data3::Check(): geometry/data normal axes have different min values:" << std::endl;
      std::cerr << "\t" << myA->GetXmin() << " " << normal->GetXmin() << std::endl;
      val = kFALSE;
    }

  if (std::abs(myA->GetXmax()-normal->GetXmax())>std::numeric_limits<double>::epsilon())
    {
      std::cerr << "Data3::Check(): geometry/data normal axes have different max values:" << std::endl;
      std::cerr << "\t" << myA->GetXmax() << " " << normal->GetXmax() << std::endl;
      val = kFALSE;
    }

  return val;
}
