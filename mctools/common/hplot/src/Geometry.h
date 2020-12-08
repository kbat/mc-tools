#ifndef Geometry_h_
#define Geometry_h_

#include "Data.h"

class Geometry : public Data {
  inline void ErrorHist(std::shared_ptr<TH2> h) const {;}
protected:
  virtual void SetH2(std::shared_ptr<TH2> h2);
  virtual void BuildMaxH2();
 public:
  Geometry(const std::string& fname,
	   const std::string& hname,
	   const std::shared_ptr<Arguments> args);
  virtual ~Geometry();

  std::string GetGOption() const {return "same " + args->GetGoption(); }
  virtual data_t GetType() const { return kGeometry; }
  virtual std::string GetTypeStr() const { return "Geometry"; }
  virtual std::shared_ptr<TH2> Draw(const Float_t val) const;
  virtual std::shared_ptr<TH2> Draw(const std::string val="") const { return Data::Draw(val); }

};

#endif
