#ifndef GeometryMultiGraph_h_
#define GeometryMultiGraph_h_

#include <TMultiGraph.h>
#include "Geometry.h"
#include "Arguments.h"

class GeometryMultiGraph : public Geometry {
 private:
  TMultiGraph *mg;
 public:
  GeometryMultiGraph(const std::string& fname,
		 const std::string& mgname,
		 const std::shared_ptr<Arguments> args);
  virtual ~GeometryMultiGraph() {;}

  virtual void Draw() const;
  void Draw(const Float_t val) const {Draw();}

};

#endif
