#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <TMath.h>
#include <TFile.h>
#include <TGaxis.h>
#include <TCanvas.h>
#include "Chrono.h"
#include "Data3.h"
#include "Error.h"

namespace {

Data3::EKind Kind(const TH3& h3)
/*!
  The type the histogram keeps its bin contents in.

  Looked up once, in the constructor: the projection loop is written for that
  type, and the TH2 it fills is of the matching one.
 */
{
  if (h3.IsA() == TH3F::Class()) return Data3::EKind::F;
  if (h3.IsA() == TH3D::Class()) return Data3::EKind::D;
  if (h3.IsA() == TH3S::Class()) return Data3::EKind::S;
  if (h3.IsA() == TH3I::Class()) return Data3::EKind::I;

  throw HPlotError(std::string("unsupported histogram class ") + h3.ClassName());
}

Plane::Index H2Indexer(const TH2& h2, Int_t nv, bool flip)
/*!
  The Index of the TH2 Data3::MakeH2() builds.

  That TH2 has no normal axis, and its x axis is the horizontal axis of the
  plane while its y axis is the vertical one - the one place that convention is
  written down is MakeH2(), which is why this is not a Plane member.

  With -flip the vertical bins are written back to front.  As a negative
  stride, that is: the whole point of folding the flip in here is that it then
  costs nothing, rather than a mirrored copy of the entire TH3.
 */
{
  const Int_t base = h2.GetBin(0,0);
  Plane::Index i{base, h2.GetBin(0,1)-base, h2.GetBin(1,0)-base, 0};

  if (flip)
    {
      i.base += i.dv*(nv+1);
      i.dv = -i.dv;
    }

  return i;
}

/*!
  The smallest and the largest bin content of a projection, and which bin each
  was found in.

  This is -v output and nothing else uses it, so it may not cost the redraw it
  reports on more than it has to: TH1::GetMinimumBin() and GetMaximumBin() are
  a pass over the histogram each, and this is the same answer in one.
 */
struct Extrema {
  Double_t min{0.0}, max{0.0};
  Int_t imin{0}, jmin{0}, imax{0}, jmax{0};
};

Extrema MinMax(const TH2& h)
{
  const Int_t nx = h.GetNbinsX();
  const Int_t ny = h.GetNbinsY();

  // the bins lie in one flat array, so walking it is an addition per bin
  const Int_t base = h.GetBin(0,0);
  const Int_t di = h.GetBin(1,0) - base;
  const Int_t dj = h.GetBin(0,1) - base;

  Extrema e;
  bool first = true;

  for (Int_t j=1; j<=ny; ++j)
    {
      Int_t g = base + dj*j + di;

      for (Int_t i=1; i<=nx; ++i, g += di)
	{
	  const Double_t v = h.GetBinContent(g);

	  if (first || (v<e.min)) { e.min = v; e.imin = i; e.jmin = j; }
	  if (first || (v>e.max)) { e.max = v; e.imax = i; e.jmax = j; }
	  first = false;
	}
    }

  return e;
}

} // namespace

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
  yrev(nullptr), args(args), plane(args->GetPlane()), h3(h3), h2max(nullptr),
  kind(Kind(*h3)), dscale(args->GetScale()), flip(args->IsFlipped()),
  maxCached(1), lastPrefetch(0)
{
  /*
    The worker threads read the arrays of the TH3 directly, so nothing below
    this constructor may change it.  A histogram still holding a fill buffer
    would spill it into those arrays on the first read, so empty it here.
  */
  if (h3->GetBuffer())
    h3->BufferEmpty();

  if (args->IsRebin())
    {
      Chrono t(args->IsVerbose(), " Data3::Rebin");
      Rebin();
    }

  offset = GetOffset(args->GetOffset());
}

Data3::~Data3()
{
  /*
    The worker threads write into histograms this object owns, so let them
    finish before those go away.  The futures would do it themselves when the
    map is destroyed - being explicit about it keeps the order from depending
    on the order the members are declared in.
  */
  for (auto& p : pending)
    p.second.done.wait();
  pending.clear();
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

Int_t Data3::RebinFactor(Int_t nbins, Int_t npixels)
/*!
  How many bins to merge into one so that no more of them are left than there
  are pixels to draw them in.

  TH3::Rebin3D() drops whatever does not make up a whole group at the end of
  the axis, and shortens the axis with it - a plot half a centimetre narrower
  than the data, with the geometry outlines still drawn over the part that went
  missing.  So a factor that divides the axis exactly is preferred, as long as
  one can be had without merging away twice as much as asked; failing that the
  smallest factor that fits is used and -v says what it costs.
 */
{
  const Int_t least = std::max<Int_t>(1, TMath::Ceil(nbins/static_cast<float>(npixels)));

  for (Int_t f=least; (f<=2*least) && (f<=nbins); ++f)
    if (nbins % f == 0)
      return f;

  return least;
}

void Data3::Rebin()
{
  /*!
    Rebin the histogram so that it is not larger than the area it is drawn in
   */

  const Int_t width = args->GetPlotWidth();
  const Int_t height = args->GetPlotHeight();

  const Int_t nh = GetHorizontalAxis()->GetNbins();
  const Int_t nv = GetVerticalAxis()->GetNbins();

  const Int_t scaleH = RebinFactor(nh, width);
  const Int_t scaleV = RebinFactor(nv, height);

  if ((scaleH>=2) || (scaleV>=2)) {
    const std::array<Int_t,3> f = plane.RebinFactors(scaleV, scaleH);
    h3->Rebin3D(f[0], f[1], f[2]);

    /*
      Rebin3D() sums the bins it merges - the plot wants their average.  The
      factor is handed to the projection rather than applied here, so that the
      TH3 is left alone: one pass over it saved, and one reason less for it to
      change while a worker thread is reading it.
    */
    dscale /= scaleH*scaleV;
  }

  if (args->IsVerbose())
    {
      std::cout << "Rebinning " << h3->GetName() << ": before: " << nh << " x " << nv;
      std::cout << "\t after: " << GetHorizontalAxis()->GetNbins() << " x " << GetVerticalAxis()->GetNbins();
      std::cout << "\t by factor " << scaleH << " x " << scaleV;
      std::cout << "\t to fit " << width << " x " << height << " pixels" << std::endl;

      // see RebinFactor(): what did not make up a whole group is gone
      if (nh%scaleH)
	std::cout << "Warning: the last " << nh%scaleH
		  << " bins of the horizontal axis are not plotted" << std::endl;
      if (nv%scaleV)
	std::cout << "Warning: the last " << nv%scaleV
		  << " bins of the vertical axis are not plotted" << std::endl;
    }
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

  /*
    The replacement axis is placed in the user coordinates of the pad, which
    ROOT only works out when it paints the frame - so the first one costs a
    paint of its own.  Only the first: the axis is the same for every slice,
    and painting here again doubled the cost of every -flipwithaxis redraw,
    the pad being repainted a moment later anyway by whoever asked for it.
  */
  if (!yrev)
    {
      gPad->Update();
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

  switch (kind) {
  case EKind::F:
    h2 = std::make_shared<TH2F>(name.data(), title.data(), nh, hmin, hmax, nv, vmin, vmax);
    break;
  case EKind::D:
    h2 = std::make_shared<TH2D>(name.data(), title.data(), nh, hmin, hmax, nv, vmin, vmax);
    break;
  case EKind::S:
    h2 = std::make_shared<TH2S>(name.data(), title.data(), nh, hmin, hmax, nv, vmin, vmax);
    break;
  case EKind::I:
    h2 = std::make_shared<TH2I>(name.data(), title.data(), nh, hmin, hmax, nv, vmin, vmax);
    break;
  }

  // the shared_ptr owns the histogram - keep ROOT from deleting it as well
  h2->SetDirectory(nullptr);

  return h2;
}

std::shared_ptr<TH2> Data3::MakeSlice(Int_t bin) const
/*!
  The empty projection a Job fills in.

  Everything here is a ROOT call, and everything in Job is not: that is the
  line the worker threads may not cross.
 */
{
  const TAxis *na = GetNormalAxis();

  std::string h2name, h2title;

  if (args->IsMax())
    {
      h2name  = Form("%s_max", h3->GetName());
      h2title = "max";
    }
  else
    {
      h2name  = Form("%s_%d", h3->GetName(), bin);
      h2title = Form("%g< %c < %g",
		     na->GetBinLowEdge(bin), AxisName(plane.Normal()),
		     na->GetBinUpEdge(bin));
    }

  std::shared_ptr<TH2> h2 = MakeH2(h2name, h2title);

  // TH1::SetBinError() would allocate this on its first call - the projection
  // loop writes the array itself, so it has to exist before it starts
  h2->Sumw2();

  return h2;
}

Data3::Job Data3::MakeJob(TH2& h2, Int_t bin) const
{
  Job j;

  j.i3 = plane.Indexer(*h3);
  j.i2 = H2Indexer(h2, GetVerticalAxis()->GetNbins(), flip);

  j.nv = GetVerticalAxis()->GetNbins();
  j.nh = GetHorizontalAxis()->GetNbins();
  j.nn = GetNormalAxis()->GetNbins();
  j.nbin = bin;

  j.scale = dscale;
  j.cut = MaxErr(*args);
  j.max = args->IsMax();
  j.kind = kind;

  // a histogram without one takes the error of a bin from its content instead
  j.ein = h3->GetSumw2N() ? h3->GetSumw2()->GetArray() : nullptr;
  j.eout = h2.GetSumw2()->GetArray();

  switch (kind) {
  case EKind::F:
    j.in  = static_cast<TH3F&>(*h3).GetArray();
    j.out = static_cast<TH2F&>(h2).GetArray();
    break;
  case EKind::D:
    j.in  = static_cast<TH3D&>(*h3).GetArray();
    j.out = static_cast<TH2D&>(h2).GetArray();
    break;
  case EKind::S:
    j.in  = static_cast<TH3S&>(*h3).GetArray();
    j.out = static_cast<TH2S&>(h2).GetArray();
    break;
  case EKind::I:
    j.in  = static_cast<TH3I&>(*h3).GetArray();
    j.out = static_cast<TH2I&>(h2).GetArray();
    break;
  }

  return j;
}

template <class T>
Long64_t Data3::Run(const Job& j)
/*!
  Project one slice - or, with -max, the whole normal axis at once.

  Both histograms are walked by their global bin number, which changes by a
  constant amount per bin along each direction of the plane (Plane::Index), so
  the mapping costs one addition per bin instead of a GetBin() and a handful of
  virtual calls.  Nothing here is a ROOT call, which is what makes it safe to
  run on a worker thread.
 */
{
  const T *in = static_cast<const T*>(j.in);
  T *out = static_cast<T*>(j.out);

  Long64_t entries = 0;

  // TH1::Scale() multiplies the sums of squared weights by c*c, so the errors
  // by |c|.  A histogram without them has TH1::GetBinError() take the square
  // root of the content itself - of the scaled content, that is
  const Double_t escale = std::abs(j.scale);

  auto value = [&j,in](Int_t g)
    { return j.scale * static_cast<Double_t>(in[g]); };

  auto error = [&j,escale](Int_t g, Double_t val)
    { return j.ein ? escale*std::sqrt(j.ein[g]) : std::sqrt(std::abs(val)); };

  if (!j.max)
    {
      for (Int_t v=1; v<=j.nv; ++v)
	{
	  Int_t g3 = j.i3(v, 1, j.nbin);
	  Int_t g2 = j.i2(v, 1);

	  for (Int_t h=1; h<=j.nh; ++h, g3 += j.i3.dh, g2 += j.i2.dh)
	    {
	      const Double_t val = value(g3);
	      const Double_t err = error(g3, val);

	      if (!j.cut(val, err))
		continue;

	      out[g2] = static_cast<T>(val);
	      j.eout[g2] = err*err;
	      ++entries;
	    }
	}

      return entries;
    }

  /*
    -max: the largest value found along the normal axis, and the error of the
    bin it was found in.  Bins failing the -maxerror cut are ignored.

    The normal axis is the outermost loop, so that each pass over the
    accumulators reads one contiguous slab of the TH3 rather than striding
    across the whole of it once per bin of the plane.
  */
  const size_t ncells = static_cast<size_t>(j.nv)*j.nh;
  std::vector<Double_t> maxv(ncells, 0.0), errv(ncells, 0.0);

  for (Int_t n=1; n<=j.nn; ++n)
    for (Int_t v=1; v<=j.nv; ++v)
      {
	Int_t g3 = j.i3(v, 1, n);
	size_t k = static_cast<size_t>(v-1)*j.nh;

	for (Int_t h=1; h<=j.nh; ++h, g3 += j.i3.dh, ++k)
	  {
	    const Double_t val = value(g3);
	    const Double_t err = error(g3, val);

	    if (j.cut(val, err) && (maxv[k]<val))
	      {
		maxv[k] = val;
		errv[k] = err;
	      }
	  }
      }

  for (Int_t v=1; v<=j.nv; ++v)
    {
      Int_t g2 = j.i2(v, 1);
      size_t k = static_cast<size_t>(v-1)*j.nh;

      for (Int_t h=1; h<=j.nh; ++h, g2 += j.i2.dh, ++k)
	if (maxv[k]>0.0)
	  {
	    out[g2] = static_cast<T>(maxv[k]);
	    j.eout[g2] = errv[k]*errv[k];
	    ++entries;
	  }
    }

  return entries;
}

Long64_t Data3::Job::operator()() const
{
  switch (kind) {
  case EKind::F: return Data3::Run<Float_t>(*this);
  case EKind::D: return Data3::Run<Double_t>(*this);
  case EKind::S: return Data3::Run<Short_t>(*this);
  case EKind::I: return Data3::Run<Int_t>(*this);
  }

  return 0;
}

void Data3::Finish(const std::shared_ptr<TH2>& h2, Long64_t entries) const
/*!
  Dress a filled projection - the part of the work that talks to ROOT, and so
  never runs on a worker thread.
 */
{
  // TH1::SetBinContent() counts an entry, and the projection wrote the array
  // itself: give the histogram back the count it would have had
  h2->SetEntries(entries);

  SetH2(h2);

  if (args->IsErrors())
    ErrorHist(h2);
}

std::shared_ptr<TH2> Data3::BuildH2(Int_t bin) const
/*!
  Project the TH3 onto the plane at the given bin of the normal axis, here and
  now rather than on a worker thread
 */
{
  std::shared_ptr<TH2> h2 = MakeSlice(bin);

  Finish(h2, MakeJob(*h2, bin)());

  return h2;
}

void Data3::Launch(Int_t bin) const
/*!
  Start projecting the given slice on a worker thread, unless it is already in
  hand, already under way, or there are enough threads busy already
 */
{
  if (vh2[bin-1] || pending.count(bin))
    return;

  // the projections already under way are the ones the slider is closest to
  // needing
  if (pending.size() >= maxPending)
    return;

  Slice s;
  s.h2 = MakeSlice(bin);                // every ROOT call is here
  const Job job = MakeJob(*s.h2, bin);  // and none of them below
  s.done = std::async(std::launch::async, [job] { return job(); }).share();

  pending[bin] = std::move(s);
}

void Data3::Harvest() const
/*!
  Collect the projections the worker threads have finished, so that Launch()
  can tell how many of them are still busy
 */
{
  for (auto it = pending.begin(); it != pending.end(); )
    {
      if (it->second.done.wait_for(std::chrono::seconds(0)) != std::future_status::ready)
	{
	  ++it;
	  continue;
	}

      Finish(it->second.h2, it->second.done.get());
      vh2[it->first-1] = it->second.h2;
      Touch(it->first);

      it = pending.erase(it);
    }
}

size_t Data3::Budget() const
/*!
  How many projections may be kept.

  One per bin of the normal axis is no bound at all: a few hundred slices of a
  rebinned histogram already come to a gigabyte.  Three is the least that makes
  sense - the slice on the screen, and the two Prefetch() is about to hand over.
 */
{
  const size_t cells = static_cast<size_t>(GetHorizontalAxis()->GetNbins()+2) *
                       (GetVerticalAxis()->GetNbins()+2);
  // the contents, at most eight bytes each, and the sums of squared weights
  const size_t bytes = cells * 2*sizeof(Double_t);

  return std::max<size_t>(3, cacheBudget/std::max<size_t>(1, bytes));
}

void Data3::Touch(Int_t bin) const
/*!
  Note that this projection has just been used, and release the one that has
  not been for the longest time.

  Moving it to the back rather than counting it again is what keeps scrolling
  back and forth over the same few slices from rebuilding any of them.  Only
  this object's reference is dropped, so the slice on the canvas - which
  MainFrame holds - survives being evicted.
 */
{
  lru.erase(std::remove(lru.begin(), lru.end(), bin), lru.end());
  lru.push_back(bin);

  while (lru.size() > maxCached)
    {
      vh2[lru.front()-1].reset();
      lru.pop_front();
    }
}

Int_t Data3::NormalBin(Float_t val) const
{
  const TAxis *a = GetNormalAxis();
  const Int_t nbins = a->GetNbins();

  // the offset may fall into the underflow/overflow bin, e.g. when the slider
  // sits exactly on the edge of the axis
  return std::min(nbins, std::max(1, a->FindBin(val)));
}

std::shared_ptr<TH2> Data3::Projection(Int_t bin) const
/*!
  The projection of the given slice: the one already in hand, the one a worker
  thread is busy with, or - failing both - one made here and now
 */
{
  Harvest();

  if (!vh2[bin-1])
    {
      const auto running = pending.find(bin);
      if (running != pending.end())
	{
	  Chrono t(args->IsVerbose(), " Data3: wait for the projection");
	  Finish(running->second.h2, running->second.done.get());
	  vh2[bin-1] = running->second.h2;
	  pending.erase(running);
	}
      else
	{
	  Chrono t(args->IsVerbose(), " Data3: project");
	  vh2[bin-1] = BuildH2(bin);
	}
    }

  // Touch() may release another slice, so take this one first
  const std::shared_ptr<TH2> h2 = vh2[bin-1];
  Touch(bin);

  return h2;
}

void Data3::Prefetch(Float_t val) const
/*!
  The slider moves on to a neighbouring slice far more often than anywhere
  else, so project them while the user is looking at this one.

  Which neighbours depends on where it came from: once it is going one way, the
  next two slices that way are wanted and the one behind is not.  maxPending is
  the whole queue, so a projection that will not be looked at does not merely
  waste a core - it keeps the one that will be from starting.

  Nothing to do with -max: the whole normal axis is already in the plot.
 */
{
  if (h2max)
    return;

  Harvest();

  const Int_t nn = GetNormalAxis()->GetNbins();
  const Int_t bin = NormalBin(val);

  const Int_t dir = (bin>lastPrefetch) - (bin<lastPrefetch);
  lastPrefetch = bin;

  // both sides while there is no direction yet - at start-up, or when the
  // slider was let go where it already was
  const std::array<Int_t,2> next = dir ? std::array<Int_t,2>{bin+dir, bin+2*dir}
                                       : std::array<Int_t,2>{bin+1, bin-1};

  for (const Int_t b : next)
    if ((b >= 1) && (b <= nn))
      Launch(b);
}

void Data3::Project()
{
  if (args->IsMax())
    {
      Chrono t(args->IsVerbose(), " Data3: max projection");
      h2max = BuildH2(1); // the whole normal axis at once - see Data3::Run()
      return;
    }

  // The individual projections are built by GetH2() when they are first
  // asked for - only one of them is on screen at any time.
  vh2.assign(GetNormalAxis()->GetNbins(), nullptr);
  maxCached = Budget();
  lastPrefetch = NormalBin(offset);

  if (args->IsVerbose())
    std::cout << "Projections: at most " << maxCached << " of "
	      << vh2.size() << " slices kept" << std::endl;

  /*
    The first one now, while the geometry is being cut on a worker thread -
    Application starts that cut before calling us.
  */
  Projection(NormalBin(offset));

  return;
}

Float_t Data3::GetOffset(const std::string& val) const
/*!
  The -offset argument as a position on the normal axis: either a number, or
  one of the names of a bin of that axis.

  The names are tried first, so that std::stof() is asked only about something
  that is meant to be a number - and anything it cannot make one of is an error
  rather than a warning.  Silently plotting the slice at zero instead is worse
  than not plotting at all: the picture looks exactly like a good one.
 */
{
  const TAxis *a = GetNormalAxis();

  if (val == "centre")
    return (a->GetXmax()+a->GetXmin())/2.0;
  else if (val == "min")
    return a->GetBinCenter(1);
  else if (val == "max")
    return a->GetBinCenter(a->GetLast());

  try {
    return std::stof(val);
  }
  catch (const std::invalid_argument&) {
    throw HPlotError("offset: neither a number nor one of centre, min, max: " + val);
  }
  catch (const std::out_of_range&) {
    throw HPlotError("offset: number out of range: " + val);
  }
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

  return Projection(NormalBin(val));
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
      // timed like everything else -v reports, so that the pass it takes over
      // the projection is not silently added to the redraw it is describing
      Chrono t(true, " Data3: min/max");

      const TAxis *ax = h2->GetXaxis();
      const TAxis *ay = h2->GetYaxis();
      const Extrema e = MinMax(*h2);

      std::cout << "min: " << e.min
		<< " at (" << ax->GetBinCenter(e.imin) << ", " << ay->GetBinCenter(e.jmin) << ")\t"
		<< "max: " << e.max
		<< " at (" << ax->GetBinCenter(e.imax) << ", " << ay->GetBinCenter(e.jmax) << ")"
		<< std::endl;
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
