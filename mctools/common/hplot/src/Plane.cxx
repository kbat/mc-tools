#include <algorithm>
#include <array>
#include <iostream>
#include <stdexcept>

#include <TH3.h>

#include <boost/program_options.hpp>

#include "Plane.h"

namespace {

  /// The six accepted plane names
  const std::array<std::string,6> planes{"xy", "xz", "yx", "yz", "zx", "zy"};

  Axis ToAxis(char c)
  {
    switch (c) {
    case 'x': return Axis::X;
    case 'y': return Axis::Y;
    case 'z': return Axis::Z;
    }
    throw std::invalid_argument(std::string("Plane: unknown axis '") + c + "'");
  }

}

char AxisName(Axis a)
{
  switch (a) {
  case Axis::X: return 'x';
  case Axis::Y: return 'y';
  case Axis::Z: return 'z';
  }
  return '?';
}

bool Plane::IsValid(const std::string& val)
{
  return std::find(planes.begin(), planes.end(), val) != planes.end();
}

Plane::Plane(const std::string& val)
{
  if (!IsValid(val))
    throw std::invalid_argument("Plane: unknown projection plane: " + val);

  vertical_   = ToAxis(val[0]);
  horizontal_ = ToAxis(val[1]);

  // the normal is whichever axis is left over
  const unsigned sum = static_cast<unsigned>(Axis::X) +
                       static_cast<unsigned>(Axis::Y) +
                       static_cast<unsigned>(Axis::Z);
  normal_ = static_cast<Axis>(sum -
                              static_cast<unsigned>(vertical_) -
                              static_cast<unsigned>(horizontal_));
}

std::string Plane::GetValue() const
{
  return std::string{AxisName(vertical_), AxisName(horizontal_)};
}

std::ostream& operator<<(std::ostream& os, const Plane& p)
{
  os << p.GetValue();
  return os;
}

TAxis *GetAxis(TH3& h3, Axis a)
{
  switch (a) {
  case Axis::X: return h3.GetXaxis();
  case Axis::Y: return h3.GetYaxis();
  case Axis::Z: return h3.GetZaxis();
  }
  return nullptr;
}

void validate(boost::any& v, const std::vector<std::string>& values, Plane*, int)
{
  using namespace boost::program_options;

  // Make sure no previous assignment to 'v' was made.
  validators::check_first_occurrence(v);

  // Extract the first string from 'values'. If there is more than
  // one string, it's an error, and exception will be thrown.
  const std::string& s = validators::get_single_string(values);

  if (!Plane::IsValid(s)) {
    std::cerr << "plane: " << s << std::endl;
    throw validation_error(validation_error::invalid_option_value);
  }

  v = boost::any(Plane(s));
}
