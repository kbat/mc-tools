#ifndef Geometry_h_
#define Geometry_h_

#include "Data.h"
#include "Arguments.h"

class Geometry {
 public:
  Geometry(const std::string&,const std::string&,const std::shared_ptr<Arguments>);
  virtual ~Geometry() {;}
  //  virtual void Project() {;}
  virtual void Draw() {;}

};

#endif
