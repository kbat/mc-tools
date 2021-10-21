#ifndef Geometry3_h_
#define Geometry3_h_

#include "Geometry.h"
#include "Data3.h"

class Geometry3 : public Geometry, public Data3 {
  inline void ErrorHist(std::shared_ptr<TH2> h) const {;}
protected:
  virtual void SetH2(std::shared_ptr<TH2> h2);
  virtual void BuildMaxH2();
 public:
  Geometry3(const std::string& fname,
	   const std::string& hname,
	   const std::shared_ptr<Arguments> args);
  virtual ~Geometry3();

  std::string GetGOption() const {return "same " + args->GetGoption(); }
  virtual data_t GetType() const { return kGeometry3; }
  virtual std::string GetTypeStr() const { return "Geometry3"; }
  virtual std::shared_ptr<TH2> Draw(const Float_t val) const;
  virtual std::shared_ptr<TH2> Draw(const std::string val="") const { return Data3::Draw(val); }

};

#endif
