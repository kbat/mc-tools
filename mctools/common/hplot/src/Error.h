#ifndef Error_h_
#define Error_h_

#include <stdexcept>
#include <string>

/*!
  Any condition hplot reports to the user and gives up on.

  Thrown instead of calling exit() from deep inside the code, so that the
  classes can be used without terminating the process and main() has a single
  place where errors are reported.
*/
class HPlotError : public std::runtime_error {
 public:
  explicit HPlotError(const std::string& what) : std::runtime_error(what) {}
};

#endif
