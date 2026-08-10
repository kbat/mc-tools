#ifndef GeometryMultiGraph_h_
#define GeometryMultiGraph_h_

#include <memory>

#include <TMultiGraph.h>

#include "Data3.h"
#include "Geometry.h"
#include "Arguments.h"

/*!
  Geometry given as a set of contours, as produced by the FLUKA PLOTGEOM card.

  The contours are a single projection: unlike Geometry3 there is nothing to
  select along the normal axis, so the offset is ignored.
*/
class GeometryMultiGraph : public Geometry {
 private:
  TMultiGraph *mg;
  std::shared_ptr<Data3> data;
  void Flip();

 public:
  GeometryMultiGraph(TMultiGraph *mg,
		     const std::shared_ptr<Arguments> args,
		     const std::shared_ptr<Data3> d);
  virtual ~GeometryMultiGraph() = default;

  void Draw() override;
  void Draw(Float_t offset) override { (void)offset; Draw(); }
  std::string StatusText(Double_t x, Double_t y) const override;
};

#endif
