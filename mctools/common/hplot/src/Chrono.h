#ifndef Chrono_h_
#define Chrono_h_

#include <chrono>
#include <iostream>
#include <string>
#include <utility>

/*!
  Reports how long its scope took, but only when the -v option was given.

    {
      Chrono t(args->IsVerbose(), "Data3::Project");
      ...
    }                                 // prints "Data3::Project: 12 ms"
*/
class Chrono {
 private:
  const bool verbose;
  const std::string msg;
  const std::chrono::high_resolution_clock::time_point start;

 public:
  Chrono(bool verbose, std::string msg) :
    verbose(verbose), msg(std::move(msg)),
    start(std::chrono::high_resolution_clock::now())
  {}

  ~Chrono()
  {
    if (!verbose)
      return;

    const auto delta = std::chrono::high_resolution_clock::now() - start;
    std::cout << msg << ": "
	      << std::chrono::duration_cast<std::chrono::milliseconds>(delta).count()
	      << " ms" << std::endl;
  }

  Chrono(const Chrono&) = delete;
  Chrono& operator=(const Chrono&) = delete;
};

#endif
