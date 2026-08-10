#ifndef Plane_h_
#define Plane_h_

#include <array>
#include <string>
#include <vector>
#include <iosfwd>

#include <Rtypes.h>
#include <boost/any.hpp>

class TH3;
class TAxis;

/// One of the three axes of a TH3
enum class Axis : unsigned { X = 0, Y = 1, Z = 2 };

char AxisName(Axis a);

/*!
  The projection plane.

  The ROOT notation is used: for a plane "vh" the first character names the
  vertical axis of the resulting TH2 (that is, its y axis) and the second one
  names the horizontal axis (its x axis).  The third axis is normal to the
  plane - it is the one the -offset value and the slider run along.

  Everything that needs to know how the TH3 bins map onto the TH2 goes through
  Bin3(), so that the mapping is written down exactly once.
*/
class Plane {
 private:
  Axis vertical_;
  Axis horizontal_;
  Axis normal_;

 public:
  Plane() : vertical_(Axis::X), horizontal_(Axis::Y), normal_(Axis::Z) {}
  explicit Plane(const std::string& val);

  /// True if val is one of the six accepted plane names
  static bool IsValid(const std::string& val);

  Axis Vertical()   const { return vertical_; }
  Axis Horizontal() const { return horizontal_; }
  Axis Normal()     const { return normal_; }

  std::string GetValue() const;
  operator std::string() const { return GetValue(); }

  /*!
    TH3 bin numbers (i,j,k) of the bin at the given vertical, horizontal and
    normal position.
  */
  std::array<Int_t,3> Bin3(Int_t v, Int_t h, Int_t n) const
  {
    std::array<Int_t,3> b{};
    b[static_cast<unsigned>(vertical_)]   = v;
    b[static_cast<unsigned>(horizontal_)] = h;
    b[static_cast<unsigned>(normal_)]     = n;
    return b;
  }

  /*!
    TH3::Rebin3D() group sizes which merge v bins along the vertical axis and
    h bins along the horizontal one, leaving the normal axis untouched.
  */
  std::array<Int_t,3> RebinFactors(Int_t v, Int_t h) const { return Bin3(v,h,1); }

  friend std::ostream& operator<<(std::ostream& os, const Plane& p);
};

/// The requested axis of h3
TAxis *GetAxis(TH3& h3, Axis a);

/// Called by boost::program_options to parse and validate the -plane argument
void validate(boost::any& v, const std::vector<std::string>& values, Plane*, int);

#endif
