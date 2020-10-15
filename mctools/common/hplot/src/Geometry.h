#ifndef Geometry_h_
#define Geometry_h_

#include "Data.h"

class Geometry : public Data {
protected:
  virtual void SetH2(std::shared_ptr<TH2> h2);
 public:
  Geometry(const std::string& fname,
	   const std::string& hname,
	   const Arguments *args);
  virtual ~Geometry();
};

#endif
