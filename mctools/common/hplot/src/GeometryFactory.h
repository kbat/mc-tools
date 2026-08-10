#ifndef GeometryFactory_h_
#define GeometryFactory_h_

#include <memory>

#include "Arguments.h"
#include "Data3.h"
#include "Geometry.h"

/*!
  Build the geometry described by the -gfile/-ghist arguments, deciding from
  the type of the stored object which kind it is.

  Returns nullptr if no geometry file was given.  The returned geometry is
  ready to be drawn: it has been projected and checked against the data.
*/
std::shared_ptr<Geometry> MakeGeometry(const std::shared_ptr<Arguments>& args,
				       const std::shared_ptr<Data3>& data);

#endif
