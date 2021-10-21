#ifndef GeometryMultiGraph_h_
#define GeometryMultiGraph_h_

#include <Data3.h>
#include <TMultiGraph.h>
#include "Geometry.h"
#include "Arguments.h"

class GeometryMultiGraph : public Geometry {
 private:
  TMultiGraph *mg;
  std::shared_ptr<Data3> data;
  void Flip();
 public:
  GeometryMultiGraph(const std::string& fname,
		     const std::string& mgname,
		     const std::shared_ptr<Arguments> args,
		     const std::shared_ptr<Data3> d);
  virtual ~GeometryMultiGraph() {;}

  virtual void Draw() const;
  void Draw(const Float_t val) const {Draw();}
};

#endif
