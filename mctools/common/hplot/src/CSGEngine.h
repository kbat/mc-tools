#ifndef CSGEngine_h_
#define CSGEngine_h_

#include <memory>
#include <string>
#include <vector>

/*!
  One boundary polyline of a cut through the geometry.

  The coordinates are the plotted ones, in cm: h runs along the horizontal
  axis of the projection plane, v along its vertical axis - so they go into a
  TGraph unchanged.
*/
struct CSGPolyline {
  std::vector<double> h, v;
  std::string title; ///< the two regions the boundary separates, "A | B"
};

/*!
  A cut through the geometry: which plane, where, over which rectangle, and how
  finely it is sampled.

  The axes are named the way Plane names them - haxis is the horizontal axis of
  the plot, vaxis the vertical one - as plain indices (0=x, 1=y, 2=z), so that
  this header stays free of both ROOT and the CSG engine.
*/
struct CSGCut {
  unsigned haxis = 0, vaxis = 1;
  double offset = 0.0;              ///< position along the remaining (normal) axis, cm
  double hmin = 0.0, hmax = 0.0;    ///< sampled range along haxis, cm
  double vmin = 0.0, vmax = 0.0;    ///< sampled range along vaxis, cm
  int    nh = 2000, nv = 2000;      ///< sample cells along haxis and vaxis
  int    refine = 20;               ///< bisection steps placing a point on the boundary
  double simplify = 0.0;            ///< Douglas-Peucker tolerance in cm; 0 = off
};

/*!
  The CSG geometry of a Monte Carlo input file, and the boundaries of its
  regions on a plane cut through it.

  A thin wrapper around the csg.h/csgcontour.h headers; it is the only place they are
  compiled, since they must stay within one translation unit.  Neither of them
  knows about ROOT, which is why the contours are handed back as plain point
  lists and turned into a TMultiGraph elsewhere.

  Load() is the expensive part of the file, Contours() the expensive part of
  every view; both are safe to run on a worker thread as long as it is the only
  one using this object, and Contours() is itself threaded.  RegionAt() is not:
  it keeps the buffers it culls into between calls, so that following the mouse
  does not allocate, and only the main thread ever asks it anything.
*/
class CSGEngine {
 public:
  CSGEngine();
  ~CSGEngine();
  CSGEngine(const CSGEngine&) = delete;
  CSGEngine& operator=(const CSGEngine&) = delete;

  /// Parse a FLUKA, MCNP or PHITS input file (the format is auto-detected)
  void Load(const std::string& fname);

  /// Name of the loaded file, as given to Load()
  const std::string& GetFileName() const;

  /*!
    Region boundaries of the given cut, always in merge-materials mode: a
    boundary between two regions made of the same material is not a boundary
    anybody wants to see drawn on top of a dose map.

    nthreads<=0 asks for one worker per core.
  */
  std::vector<CSGPolyline> Contours(const CSGCut& cut, int nthreads = 0) const;

  /*!
    The region containing the given point of the cut plane, as "name (material)".
    Empty if the point is outside the geometry.
  */
  std::string RegionAt(unsigned haxis, unsigned vaxis, double offset,
		       double h, double v) const;

  /// Number of regions read from the input file
  size_t GetNRegions() const;

 private:
  struct Impl;
  std::unique_ptr<Impl> impl;
};

#endif
