#ifndef Data_h
#define Data_h

#include <chrono>
#include "Arguments.h"

class Data {
 protected:
  const std::shared_ptr<Arguments> args;

public:
  Data(const std::string& fname,
       const std::string& nname,
       const std::shared_ptr<Arguments> args);
  virtual ~Data() {;}

  void PrintChrono(std::chrono::system_clock::time_point start, std::string msg) const;
};

#endif
