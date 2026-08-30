#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <sys/stat.h>
#include <unistd.h>

#include <TColor.h>
#include <TFile.h>
#include <TGraph.h>
#include <TMacro.h>

#include "Chrono.h"
#include "Error.h"
#include "GeometryCSG.h"

namespace {

/// The file name without its directory and without its extension
std::string Stem(const std::string& path)
{
  const size_t slash = path.find_last_of('/');
  const std::string base = (slash == std::string::npos) ? path : path.substr(slash+1);

  const size_t dot = base.find_last_of('.');

  return ((dot == std::string::npos) || (dot == 0)) ? base : base.substr(0, dot);
}

bool IsFile(const std::string& path)
{
  struct stat st;

  return (stat(path.data(), &st) == 0) && S_ISREG(st.st_mode);
}

/// An empty file of our own in the temporary directory
std::string MakeTempFile()
{
  const char *tmpdir = getenv("TMPDIR");
  std::string path = std::string(tmpdir ? tmpdir : "/tmp") + "/hplot-geometry-XXXXXX";

  const int fd = mkstemp(&path[0]);
  if (fd < 0)
    throw HPlotError("can not create a temporary file " + path);
  close(fd);

  return path;
}

} // namespace

GeometryCSG::GeometryCSG(const std::shared_ptr<Arguments> args,
			 const std::shared_ptr<Data3> data) :
  args(args), data(data), cached(0), drawn(nullptr), drawnOffset(0.0), drawnBin(0)
{
  const std::string fname = InputFile();

  {
    Chrono t(args->IsVerbose(), " GeometryCSG: read " + fname);
    engine.Load(fname);
  }

  if (args->IsVerbose())
    std::cout << "Geometry: " << engine.GetNRegions() << " regions read from "
	      << fname << std::endl;

  SetUpCut();

  drawnOffset = CutOffset(data->GetOffset());
  drawnBin = data->GetNormalAxis()->FindBin(drawnOffset);
}

GeometryCSG::~GeometryCSG()
{
  /*
    The worker threads read the engine, which is about to go away, so let them
    finish first.  The futures would do this by themselves when the map is
    destroyed - being explicit about it keeps the order from depending on the
    order the members are declared in.
  */
  for (auto& p : pending)
    p.second.wait();
  pending.clear();

  if (!tmpfile.empty())
    unlink(tmpfile.data());
}

std::string GeometryCSG::InputFile()
/*!
  The Monte Carlo input file to cut.

  The gfile argument is the file itself when a file of that name exists.
  Otherwise its stem names a TMacro inside the data file which holds the input
  file - the copy fluka2root stores there - and that is written out to a
  temporary file, since the geometry parser reads files rather than strings.
 */
{
  const std::string gfile = args->GetGeoFile();

  if (IsFile(gfile))
    return gfile;

  const std::string dfile = args->GetDataFile();
  const std::string macro = Stem(gfile);

  TFile df(dfile.data());
  if (df.IsZombie()) {
    df.Close();
    throw HPlotError("can not open " + dfile);
  }

  TMacro *m = df.Get<TMacro>(macro.data());
  if (!m) {
    df.Close();
    throw HPlotError(gfile + " is neither an existing file nor the name of a TMacro (" +
		     macro + ") in " + dfile);
  }

  tmpfile = MakeTempFile();
  m->SaveSource(tmpfile.data());
  df.Close();

  if (args->IsVerbose())
    std::cout << "Geometry: the TMacro " << macro << " of " << dfile
	      << " written to " << tmpfile << std::endl;

  return tmpfile;
}

void GeometryCSG::SetUpCut()
/*!
  Everything about the cut except where along the normal axis it is made: the
  projection plane and the sampled rectangle come from the data histogram, so
  that the outlines cover exactly what is plotted.

  The sample grid is proportional to the canvas rather than to the rectangle in
  cm, which keeps the sampling uniform in the picture - the plot is stretched
  to the canvas, and a feature is worth resolving when it is visible there.
 */
{
  const Plane& plane = data->GetPlane();
  const TAxis *ha = data->GetHorizontalAxis();
  const TAxis *va = data->GetVerticalAxis();

  cut.haxis = static_cast<unsigned>(plane.Horizontal());
  cut.vaxis = static_cast<unsigned>(plane.Vertical());

  /*
    The plotted range rather than the whole histogram, so that the samples are
    spent on what is actually shown.  With -flip these are still the geometry's
    own coordinates: the range Data3::SetH2() puts on the axis is this one
    mirrored, and MakeMultiGraph() mirrors the outlines the same way.
  */
  cut.hmin = args->IsXmin() ? args->GetXmin() : ha->GetXmin();
  cut.hmax = args->IsXmin() ? args->GetXmax() : ha->GetXmax();
  cut.vmin = args->IsYmin() ? args->GetYmin() : va->GetXmin();
  cut.vmax = args->IsYmin() ? args->GetYmax() : va->GetXmax();

  const size_t nh = args->GetGres();
  const double ratio = static_cast<double>(args->GetHeight()) / args->GetWidth();

  cut.nh = static_cast<int>(nh);
  cut.nv = std::max(1, static_cast<int>(std::lround(nh*ratio)));

  if (args->IsVerbose())
    std::cout << "Geometry: " << cut.nh << "x" << cut.nv << " sample grid over "
	      << AxisName(plane.Horizontal()) << " [" << cut.hmin << ", " << cut.hmax << "], "
	      << AxisName(plane.Vertical())   << " [" << cut.vmin << ", " << cut.vmax << "] cm"
	      << std::endl;
}

Double_t GeometryCSG::CutOffset(Float_t offset) const
/*!
  Where to cut for the data slice shown at the given offset.

  The middle of that slice: the cut is then representative of the whole slab
  the data are integrated over, and - the point of doing it here - every
  offset within one bin gives the same cut, so dragging the slider through a
  bin does not recompute anything.

  An offset outside the data histogram is used as it is: unlike the data, the
  geometry is defined there as well.
 */
{
  const TAxis *a = data->GetNormalAxis();
  const Int_t bin = a->FindBin(offset);

  return ((bin >= 1) && (bin <= a->GetNbins())) ? a->GetBinCenter(bin) : offset;
}

Double_t GeometryCSG::FlipOffset() const
/*!
  v -> FlipOffset()-v mirrors the geometry the same way Data3::Flip() mirrors
  the data, about the middle of the vertical axis.
 */
{
  const TAxis *a = data->GetVerticalAxis();

  return a->GetXmin() + a->GetXmax();
}

void GeometryCSG::Harvest() const
/*!
  Collect the cuts the worker threads have finished, so that Prefetch() can
  tell how many of them are still busy.
 */
{
  for (auto it = pending.begin(); it != pending.end(); )
    {
      if (it->second.wait_for(std::chrono::seconds(0)) != std::future_status::ready)
	{
	  ++it;
	  continue;
	}

      Store(it->first, MakeMultiGraph(it->second.get()));
      it = pending.erase(it);
    }
}

size_t GeometryCSG::Size(const TMultiGraph& mg)
/*!
  Roughly how much memory a cut takes: its points, plus what a TGraph costs
  around each polyline.

  Roughly is enough - the number decides how many cuts are kept, and nothing a
  user ever sees.
 */
{
  const TList *graphs = mg.GetListOfGraphs();
  if (!graphs)
    return 0;

  size_t bytes = 0;

  TIter next(graphs);
  while (const TObject *o = next())
    bytes += sizeof(TGraph) +
      2*sizeof(Double_t)*static_cast<const TGraph*>(o)->GetN();

  return bytes;
}

void GeometryCSG::Store(Double_t offset, const std::shared_ptr<TMultiGraph>& mg) const
{
  Cut& slot = cache[offset];

  cached -= slot.bytes; // zero for an offset that was not cached before
  slot.mg = mg;
  slot.bytes = Size(*mg);
  cached += slot.bytes;

  if (args->IsVerbose() && (cache.size() == 1))
    std::cout << "Geometry: a cut is about " << slot.bytes/1024 << " kB, so at most "
	      << std::max(minCached, cacheBudget/std::max<size_t>(1, slot.bytes))
	      << " of them are kept" << std::endl;

  Touch(offset);
}

void GeometryCSG::Touch(Double_t offset) const
/*!
  Note that this cut has just been used, and release the ones that have not
  been for the longest time.

  A cut is a TGraph per material boundary on the plane, which for a detailed
  geometry comes to megabytes; keeping one for every offset the user has ever
  scrolled past is a leak in all but name.  Moving it to the back rather than
  counting it again is what keeps scrolling back and forth over the same few
  slices from cutting any of them twice.  Only this object's reference is
  dropped, so the cut on the canvas - which drawn holds - survives eviction.
 */
{
  lru.erase(std::remove(lru.begin(), lru.end(), offset), lru.end());
  lru.push_back(offset);

  while ((cached > cacheBudget) && (lru.size() > minCached))
    {
      const auto it = cache.find(lru.front());
      if (it != cache.end())
	{
	  cached -= it->second.bytes;
	  cache.erase(it);
	}
      lru.pop_front();
    }
}

void GeometryCSG::Prefetch(Float_t offset) const
{
  Harvest();

  const Double_t off = CutOffset(offset);

  if (cache.count(off) || pending.count(off))
    return;

  // the cuts already under way are the ones the user is closest to needing
  if (pending.size() >= maxPending)
    return;

  CSGCut c = cut;
  c.offset = off;

  pending[off] = std::async(std::launch::async,
			    [this, c] { return engine.Contours(c); }).share();
}

std::shared_ptr<TMultiGraph> GeometryCSG::GetMultiGraph(Double_t offset) const
{
  const auto hit = cache.find(offset);
  if (hit != cache.end())
    {
      Touch(offset);
      return hit->second.mg;
    }

  std::shared_ptr<TMultiGraph> mg(nullptr);

  const auto running = pending.find(offset);
  if (running != pending.end())
    {
      Chrono t(args->IsVerbose(), " GeometryCSG: wait for the cut");
      mg = MakeMultiGraph(running->second.get());
      pending.erase(running);
    }
  else
    {
      Chrono t(args->IsVerbose(), " GeometryCSG: cut");
      CSGCut c = cut;
      c.offset = offset;
      mg = MakeMultiGraph(engine.Contours(c));
    }

  Store(offset, mg);

  return mg;
}

std::shared_ptr<TMultiGraph> GeometryCSG::MakeMultiGraph(const std::vector<CSGPolyline>& polylines) const
{
  auto mg = std::make_shared<TMultiGraph>("geometry", "geometry");

  const Int_t col = TColor::GetColor(args->GetGlcolor().data());
  const Float_t alpha = args->GetGlalpha();
  const Width_t width = args->GetGlwidth();

  const bool flip = args->IsFlipped();
  const Double_t vflip = flip ? FlipOffset() : 0.0;

  Int_t i = 0;
  for (const CSGPolyline& p : polylines)
    {
      const Int_t n = static_cast<Int_t>(p.h.size());

      TGraph *gr = new TGraph(n);
      for (Int_t j=0; j<n; ++j)
	gr->SetPoint(j, p.h[j], flip ? vflip-p.v[j] : p.v[j]);

      gr->SetName(Form("g%d", i++));
      gr->SetTitle(p.title.data());
      gr->SetLineWidth(width);
      gr->SetLineColorAlpha(col, alpha);
      gr->SetMarkerColorAlpha(col, alpha);

      mg->Add(gr, "l"); // the TMultiGraph takes ownership
    }

  return mg;
}

void GeometryCSG::Draw(Float_t offset)
{
  const Double_t off = CutOffset(offset);
  const TAxis *a = data->GetNormalAxis();
  const Int_t bin = a->FindBin(off);
  const Int_t was = drawnBin;

  drawn = GetMultiGraph(off);
  drawn->Draw("l");
  drawnOffset = off;
  drawnBin = bin;

  /*
    The slider is most likely to move on to one of the neighbouring slices, so
    cut them while the user is looking at this one.  Nothing to do when there
    is no slider: with -max the whole normal axis is already in the plot.
  */
  if (args->IsMax())
    return;

  /*
    Once the user is scrolling, the two neighbours are no longer equally
    likely: the next two cuts in the same direction are.  Which matters more
    than it looks, because a cut cannot be called off once it has started - the
    engine offers no way of interrupting one - so cutting a slice that will not
    be looked at does not merely waste a core, it holds up the slice that will
    be: maxPending is the whole queue.  Both sides only when there is no
    direction yet, at start-up or after the slider was dragged back to where it
    already was.
  */
  const Int_t dir = (bin>was) - (bin<was);
  const std::array<Int_t,2> next = dir ? std::array<Int_t,2>{bin+dir, bin+2*dir}
                                       : std::array<Int_t,2>{bin+1, bin-1};

  for (const Int_t b : next)
    if ((b >= 1) && (b <= a->GetNbins()))
      Prefetch(a->GetBinCenter(b));
}

std::string GeometryCSG::StatusText(Double_t x, Double_t y) const
{
  const Double_t v = args->IsFlipped() ? FlipOffset()-y : y;

  const std::string region = engine.RegionAt(cut.haxis, cut.vaxis, drawnOffset, x, v);

  return region.empty() ? "outside the geometry" : region;
}
