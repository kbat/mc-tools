#ifndef Geometry_h_
#define Geometry_h_

#include <string>

#include <Rtypes.h>

/*!
  Something drawn on top of the data histogram to show where the material
  boundaries are.

  Two kinds exist: a TH3 of material indices (Geometry3) and the set of
  contours produced by the FLUKA PLOTGEOM card (GeometryMultiGraph).  The rest
  of the program only ever talks to them through this interface.
*/
class Geometry {
 public:
  virtual ~Geometry() = default;

  /// Draw at the offset the geometry was configured with
  virtual void Draw() = 0;

  /// Draw at the given offset along the axis normal to the projection plane
  virtual void Draw(Float_t offset) = 0;

  /*!
    One line describing the geometry at the given position of the plot, shown
    in the status bar of the GUI.
  */
  virtual std::string StatusText(Double_t x, Double_t y) const = 0;
};

#endif
