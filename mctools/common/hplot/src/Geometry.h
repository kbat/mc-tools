#ifndef Geometry_h_
#define Geometry_h_

#include "Data.h"

class Geometry : public Data {
  inline void ErrorHist(std::shared_ptr<TH2> h) const {;}
protected:
  virtual void SetH2(std::shared_ptr<TH2> h2);
 public:
  Geometry(const std::string& fname,
	   const std::string& hname,
	   const Arguments *args);
  virtual ~Geometry();

  std::string GetGOption() const {return "same " + args->GetGoption(); }
  virtual std::string GetType() const { return "Geometry"; }
};

#endif
