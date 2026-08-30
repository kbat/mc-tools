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

  /*!
    Where the bin (v,h,n) of the plane sits in a histogram's global bin
    numbering, and how far apart neighbouring bins are there.

    ROOT keeps the bins of a TH2 or a TH3 in one flat array, so a step along
    any of the three directions is a constant step in that array.  The
    projection loops walk it with these strides rather than asking the
    histogram for one bin at a time, which turns the index arithmetic and the
    virtual calls of GetBinContent(i,j,k) into a single addition per bin.
  */
  struct Index {
    Int_t base{0};              ///< global bin of (v,h,n) = (0,0,0)
    Int_t dv{0}, dh{0}, dn{0};  ///< global bins per vertical/horizontal/normal bin

    Int_t operator()(Int_t v, Int_t h, Int_t n=0) const
    { return base + dv*v + dh*h + dn*n; }
  };

  /*!
    The Index of the given histogram.

    The steps are measured rather than derived: one unit step along each
    direction, handed to the histogram's own GetBin().  So the mapping from the
    plane onto the axes is still written down in Bin3() alone, and how a
    histogram numbers its bins is still known to ROOT alone.
  */
  template <class H> Index Indexer(const H& h) const
  {
    const std::array<Int_t,3> o = Bin3(0,0,0);
    const Int_t base = h.GetBin(o[0], o[1], o[2]);

    auto step = [&h,base](const std::array<Int_t,3>& b)
      { return h.GetBin(b[0], b[1], b[2]) - base; };

    return Index{base, step(Bin3(1,0,0)), step(Bin3(0,1,0)), step(Bin3(0,0,1))};
  }

  friend std::ostream& operator<<(std::ostream& os, const Plane& p);
};

/// The requested axis of h3
TAxis *GetAxis(TH3& h3, Axis a);

/// Called by boost::program_options to parse and validate the -plane argument
void validate(boost::any& v, const std::vector<std::string>& values, Plane*, int);

#endif
