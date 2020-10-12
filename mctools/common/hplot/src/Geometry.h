#ifndef Geometry_h_
#define Geometry_h_

#include "Data.h"

class Geometry : public Data {
 public:
  Geometry(const std::string& fname,
	   const std::string& hname,
	   const Arguments *args);
  virtual ~Geometry();
  virtual void SetH2();
};

#endif
