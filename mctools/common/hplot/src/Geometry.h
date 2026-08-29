#ifndef Geometry_h_
#define Geometry_h_

#include <string>

#include <Rtypes.h>

/*!
  Something drawn on top of the data histogram to show where the material
  boundaries are.

  GeometryCSG, which cuts a Monte Carlo input file on the plane the data are
  projected on, is the only implementation; the rest of the program talks to it
  through this interface.
*/
class Geometry {
 public:
  virtual ~Geometry() = default;

  /// Draw at the offset the geometry was configured with
  virtual void Draw() = 0;

  /// Draw at the given offset along the axis normal to the projection plane
  virtual void Draw(Float_t offset) = 0;

  /*!
    Move the geometry to the end of the list of primitives of the current pad,
    so that it is painted last, on top of the data.
  */
  virtual void Pop() = 0;

  /*!
    One line describing the geometry at the given position of the plot, shown
    in the status bar of the GUI.
  */
  virtual std::string StatusText(Double_t x, Double_t y) const = 0;
};

#endif
