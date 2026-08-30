/*
  The one translation unit that compiles the CSG engine.

  csg.h defines its member functions non-inline, so it may be included
  exactly once in the program; it also opens "using namespace std" at global
  scope and defines a Plane of its own, which is not the hplot Plane.  Both are
  reasons to keep every other hplot header out of this file - Error.h is the
  only one it needs, and that one declares nothing but an exception.
*/

#include "csgcontour.h"

#include <thread>

#include "CSGEngine.h"
#include "Error.h"

namespace {

/// The unit vector along axis a (0=x, 1=y, 2=z)
Vec3 UnitAxis(unsigned a)
{
  return Vec3(a == 0, a == 1, a == 2);
}

/*!
  The cut plane of a projection: U (the plane's "right") is the horizontal axis
  of the plot and V (its "up") the vertical one, so that the (u,v) coordinates
  csgcontour returns are already the plotted ones.  The remaining axis is
  normal to the cut, and buildPlane() keeps only the normal component of the
  origin, so the offset alone positions the plane.
*/
Plane CutPlane(unsigned haxis, unsigned vaxis, double offset)
{
  const unsigned naxis = 3 - haxis - vaxis;

  const Vec3 U = UnitAxis(haxis);
  const Vec3 V = UnitAxis(vaxis);
  const Vec3 O = UnitAxis(naxis) * offset;

  ViewParams vp;
  vp.rightx = U.x; vp.righty = U.y; vp.rightz = U.z;
  vp.upx    = V.x; vp.upy    = V.y; vp.upz    = V.z;
  vp.ox     = O.x; vp.oy     = O.y; vp.oz     = O.z;

  return buildPlane(vp);
}

int NThreads(int nthreads)
{
  if (nthreads > 0)
    return nthreads;

  const unsigned n = std::thread::hardware_concurrency();
  return n < 1 ? 1 : static_cast<int>(n);
}

} // namespace

struct CSGEngine::Impl {
  FlukaGeometry g;
  std::string fname;
  bool loaded = false;

  /*!
    Scratch space for RegionAt(), kept between calls so that moving the mouse
    does not allocate three vectors per event.  Only the main thread ever looks
    a region up, while Contours() keeps its working set in its own locals and
    so stays safe to run on a worker.
  */
  std::vector<char> bit;
  std::vector<int> activeBodies, candRegions;
};

CSGEngine::CSGEngine() :
  impl(std::make_unique<Impl>())
{
}

CSGEngine::~CSGEngine() = default;

void CSGEngine::Load(const std::string& fname)
{
  if (!impl->g.load(fname.data()))
    throw HPlotError("can not read the geometry from " + fname);

  if (impl->g.regions.empty())
    throw HPlotError("no regions found in " + fname);

  impl->fname = fname;
  impl->loaded = true;
}

const std::string& CSGEngine::GetFileName() const
{
  return impl->fname;
}

size_t CSGEngine::GetNRegions() const
{
  return impl->g.regions.size();
}

std::vector<CSGPolyline> CSGEngine::Contours(const CSGCut& cut, int nthreads) const
{
  if (!impl->loaded)
    throw HPlotError("CSGEngine::Contours() called before Load()");

  const Plane pl = CutPlane(cut.haxis, cut.vaxis, cut.offset);

  Window win;
  win.u0 = cut.hmin; win.u1 = cut.hmax;
  win.v0 = cut.vmin; win.v1 = cut.vmax;

  ContourOpts o;
  o.nx = std::max(1, cut.nh);
  o.ny = std::max(1, cut.nv);
  o.refine = cut.refine;
  o.simplify = cut.simplify;
  o.mergeMat = true; // boundaries between regions of one material are not shown
  o.nthreads = NThreads(nthreads);

  const std::vector<Polyline> ps = extractContours(impl->g, pl, win, o);

  auto rname = [this](int r) -> std::string {
    return (r >= 0 && r < static_cast<int>(impl->g.regions.size()))
      ? impl->g.regions[r].name : std::string("OUTSIDE");
  };

  std::vector<CSGPolyline> val;
  val.reserve(ps.size());
  for (const Polyline& p : ps)
    {
      if (p.u.size() < 2)
	continue;
      CSGPolyline c;
      c.h = p.u;
      c.v = p.v;
      c.title = rname(p.regA) + " | " + rname(p.regB);
      val.push_back(std::move(c));
    }

  return val;
}

std::string CSGEngine::RegionAt(unsigned haxis, unsigned vaxis, double offset,
				double h, double v) const
{
  if (!impl->loaded)
    return "";

  const Plane pl = CutPlane(haxis, vaxis, offset);
  const Vec3 P = pl.at(h, v);

  /*
    Culling to the single point leaves only the handful of bodies that can
    possibly matter there, so this costs one pass over the body bounding boxes
    rather than a full classification - cheap enough to run on every mouse move.
    The buffers it fills are members, so only the first call allocates them.
  */
  impl->g.cullToWindow(pl, h, v, h, v,
		       impl->bit, impl->activeBodies, impl->candRegions);

  const int r = regionAtXYculled(impl->g, impl->bit, P,
				 impl->activeBodies, impl->candRegions);
  if (r < 0 || r >= static_cast<int>(impl->g.regions.size()))
    return "";

  const Region& reg = impl->g.regions[r];

  return reg.material.empty() ? reg.name : reg.name + " (" + reg.material + ")";
}
