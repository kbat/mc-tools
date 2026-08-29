#include <iostream>
#include <TMath.h>
#include <TFile.h>
#include <TGaxis.h>
#include <TCanvas.h>
#include "Chrono.h"
#include "Data3.h"
#include "Error.h"

TH3 *Data3::ReadTH3(const std::string& fname, const std::string& hname)
{
  TFile df(fname.data());
  if (df.IsZombie()) {
    df.Close();
    throw HPlotError("can not open " + fname);
  }

  TH3 *h3(nullptr);
  df.GetObject<TH3>(hname.data(), h3);
  if (!h3) {
    df.Close();
    throw HPlotError("can not find the TH3 " + hname + " in " + fname);
  }

  h3->SetDirectory(nullptr); // detach from the file we are about to close
  df.Close();

  return h3;
}

Data3::Data3(const std::string& fname, const std::string& hname,
	     const std::shared_ptr<Arguments> args) :
  Data3(ReadTH3(fname, hname), args)
{
}

Data3::Data3(TH3 *h3, const std::shared_ptr<Arguments> args) :
  yrev(nullptr), args(args), plane(args->GetPlane()), h3(h3), h2max(nullptr)
{
  if (args->IsRebin())
    {
      Chrono t(args->IsVerbose(), " Data3::Rebin");
      Rebin();
    }

  if (args->IsFlipped())
    {
      Chrono t(args->IsVerbose(), " Data3::Flip");
      Flip();
    }

  offset = GetOffset(args->GetOffset());
}

void Data3::SetH2(std::shared_ptr<TH2> h2) const
{
  if (args->GetTitle() != "None")
    h2->SetTitle(args->GetTitle().data());
  else
    h2->SetTitle(Form("%s %s projection: %s", h3->GetTitle(),
		      plane.GetValue().data(), h2->GetTitle()));

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

  h2->SetContour(args->GetDcont());
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
  flipped->SetDirectory(nullptr); // owned by the shared_ptr, not by ROOT
  flipped->Reset();

  const Int_t nv = GetVerticalAxis()->GetNbins();
  const Int_t nh = GetHorizontalAxis()->GetNbins();
  const Int_t nn = GetNormalAxis()->GetNbins();

  for (Int_t v=1; v<=nv; ++v)
    for (Int_t h=1; h<=nh; ++h)
      for (Int_t n=1; n<=nn; ++n)
	{
	  const std::array<Int_t,3> from = plane.Bin3(v, h, n);
	  const std::array<Int_t,3> to   = plane.Bin3(nv+1-v, h, n);

	  flipped->SetBinContent(to[0], to[1], to[2],
				 h3->GetBinContent(from[0], from[1], from[2]));
	  flipped->SetBinError(to[0], to[1], to[2],
			       h3->GetBinError(from[0], from[1], from[2]));
	}

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

void Data3::Rebin()
{
  /*!
    Rebin the histogram so that it is not larger than width x height
   */

  const Int_t width = args->GetWidth();
  const Int_t height = args->GetHeight();

  const Int_t nh = GetHorizontalAxis()->GetNbins();
  const Int_t nv = GetVerticalAxis()->GetNbins();

  const Int_t scaleH =
    TMath::Ceil(nh/static_cast<float>(width));
  if (scaleH==0)
    throw HPlotError("horizontal rebin factor = 0");

  const Int_t scaleV =
    TMath::Ceil(nv/static_cast<float>(height));
  if (scaleV==0)
    throw HPlotError("vertical rebin factor = 0");

  if ((scaleH>=2) || (scaleV>=2)) {
    const std::array<Int_t,3> f = plane.RebinFactors(scaleV, scaleH);
    h3->Rebin3D(f[0], f[1], f[2]);

    {
      Chrono t(args->IsVerbose(), " Rebin: Data3 scale after rebin");
      h3->Scale(1.0/(scaleH*scaleV));
    }
  }

  if (args->IsVerbose())
    {
      std::cout << "Rebinning " << h3->GetName() << ": before: " << nh << " x " << nv;
      std::cout << "\t after: " << GetHorizontalAxis()->GetNbins() << " x " << GetVerticalAxis()->GetNbins();
      std::cout << "\t by factor " << scaleH << " x " << scaleV << std::endl;
    }
  return;
}

void Data3::BuildMaxH2()
{
  /*!
    Build the TH2 where each bin holds the largest value found along the normal
    axis, together with the error of that bin.  Bins failing the -maxerror cut
    are ignored.
  */
  std::string name = Form("%s_max", h3->GetName());
  std::string title = "max";
  h2max = MakeH2(name, title);

  const Int_t nv = GetVerticalAxis()->GetNbins();
  const Int_t nh = GetHorizontalAxis()->GetNbins();
  const Int_t nn = GetNormalAxis()->GetNbins();

  for (Int_t v=1; v<=nv; ++v)
    for (Int_t h=1; h<=nh; ++h)
      {
	Double_t max(0.0);
	Double_t err(0.0);
	for (Int_t n=1; n<=nn; ++n)
	  {
	    const std::array<Int_t,3> b = plane.Bin3(v, h, n);
	    const Double_t val = h3->GetBinContent(b[0], b[1], b[2]);
	    const Double_t e   = h3->GetBinError(b[0], b[1], b[2]);
	    if ((args->IsMaxErr(val,e)) && (max<val)) {
	      //if ((args->IsMaxErr(val,e)) && (max+err<val-e)) {
	      max = val;
	      err = e;
	    }
	  }
	if (max>0.0)
	  {
	    h2max->SetBinContent(h, v, max);
	    h2max->SetBinError(h, v, err);
	  }
      }

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


TAxis *Data3::GetNormalAxis() const
{
  return GetAxis(*h3, plane.Normal());
}

TAxis *Data3::GetHorizontalAxis() const
{
  return GetAxis(*h3, plane.Horizontal());
}

TAxis *Data3::GetVerticalAxis() const
{
  return GetAxis(*h3, plane.Vertical());
}

std::shared_ptr<TH2> Data3::MakeH2(std::string& name, std::string& title) const
/*!
  Create the TH2 histogram based on the projection plane and TH3 binning.
  The TH2 x axis is the horizontal axis of the plane, its y axis the vertical one.
 */
{
  const TAxis *va = GetVerticalAxis();
  const TAxis *ha = GetHorizontalAxis();

  const Int_t   nh = ha->GetNbins();
  const Float_t hmin = ha->GetXmin();
  const Float_t hmax = ha->GetXmax();

  const Int_t   nv = va->GetNbins();
  const Float_t vmin = va->GetXmin();
  const Float_t vmax = va->GetXmax();

  std::shared_ptr<TH2> h2(nullptr);

  if (h3->IsA() == TH3F::Class())
    h2 = std::make_shared<TH2F>(name.data(), title.data(), nh, hmin, hmax, nv, vmin, vmax);
  else if (h3->IsA() == TH3D::Class())
    h2 = std::make_shared<TH2D>(name.data(), title.data(), nh, hmin, hmax, nv, vmin, vmax);
  else if (h3->IsA() == TH3S::Class())
    h2 = std::make_shared<TH2S>(name.data(), title.data(), nh, hmin, hmax, nv, vmin, vmax);
  else if (h3->IsA() == TH3I::Class())
    h2 = std::make_shared<TH2I>(name.data(), title.data(), nh, hmin, hmax, nv, vmin, vmax);
  else
    throw HPlotError(std::string("unsupported histogram class ") + h3->ClassName());

  // the shared_ptr owns the histogram - keep ROOT from deleting it as well
  h2->SetDirectory(nullptr);

  return h2;
}


std::shared_ptr<TH2> Data3::BuildH2(Int_t bin) const
/*!
  Project the TH3 onto the plane at the given bin of the normal axis
 */
{
  const TAxis *na = GetNormalAxis();

  std::string h2name  = Form("%s_%d", h3->GetName(), bin);
  std::string h2title = Form("%g< %c < %g",
			     na->GetBinLowEdge(bin), AxisName(plane.Normal()),
			     na->GetBinUpEdge(bin));

  std::shared_ptr<TH2> h2 = MakeH2(h2name, h2title);

  const Int_t nv = GetVerticalAxis()->GetNbins();
  const Int_t nh = GetHorizontalAxis()->GetNbins();

  for (Int_t v=1; v<=nv; ++v)
    for (Int_t h=1; h<=nh; ++h)
      {
	const std::array<Int_t,3> b = plane.Bin3(v, h, bin);
	const Double_t val = h3->GetBinContent(b[0], b[1], b[2]);
	const Double_t err = h3->GetBinError(b[0], b[1], b[2]);
	if (args->IsMaxErr(val,err)) {
	  h2->SetBinContent(h, v, val);
	  h2->SetBinError(h, v, err);
	}
      }

  SetH2(h2);

  if (args->IsErrors())
    ErrorHist(h2);

  return h2;
}

void Data3::Project()
{
  {
    Chrono t(args->IsVerbose(), " Project: Data3 scale");
    h3->Scale(args->GetScale());
  }

  if (args->IsMax())
    {
      BuildMaxH2();
      return;
    }

  // The individual projections are built by GetH2() when they are first
  // asked for - only one of them is on screen at any time.
  vh2.assign(GetNormalAxis()->GetNbins(), nullptr);

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
/*!
  Return the projection at the given offset along the normal axis, building it
  on the first request.
 */
{
  if (h2max)
    return h2max;

  const TAxis *a = GetNormalAxis();
  const Int_t nbins = a->GetNbins();
  Int_t bin = a->FindBin(val);

  // the offset may fall into the underflow/overflow bin, e.g. when the slider
  // sits exactly on the edge of the axis
  if (bin>nbins)
    bin = nbins;
  else if (bin<1)
    bin = 1;

  std::shared_ptr<TH2>& h2 = vh2[bin-1];
  if (!h2)
    h2 = BuildH2(bin);

  return h2;
}

std::shared_ptr<TH2> Data3::Draw(const Float_t val) const
/*!
  Draws h2 at the given offset
 */
{
  std::shared_ptr <TH2> h2 = GetH2(val);

  h2->Draw();

  if (args->IsFlippedAxis())
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
