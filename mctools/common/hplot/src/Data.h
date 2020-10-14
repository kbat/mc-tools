#ifndef Data_h_
#define Data_h_

#include <TH3.h>
#include <TH2.h>
#include <TAxis.h>

#include "Arguments.h"

class Data {
 private:
  std::shared_ptr<TH3> h3;
  std::string plane;
  TAxis *GetHorizontalAxis() const;
  TAxis *GetVerticalAxis() const;
  std::shared_ptr<TH2> Project();
 protected:
  std::shared_ptr<TH2> h2;
  const Arguments *args;
  Float_t centre;
 public:
  /* Data(const TH3F* h3, */
  /*      const std::string& plane); */
  Data(const std::string& fname,
       const std::string& hname,
       const Arguments *args);
  virtual ~Data();
  virtual void SetH2();
  const std::shared_ptr<TH3> GetH3() const { return h3; };
  std::shared_ptr <TH2> GetH2() const { return h2; };
  TAxis *GetNormalAxis() const;
  void SetCentre(Float_t val) { centre=val; }
  Float_t GetCentre() const { return centre; }
};

#endif
