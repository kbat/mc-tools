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
 protected:
  std::vector< std::shared_ptr<TH2> > vh2;
  const Arguments *args;
  Float_t centre; // (initial) normal axis centre - can be changed with MainFrame::slider
  virtual void SetH2(std::shared_ptr<TH2> h2);
 public:
  /* Data(const TH3F* h3, */
  /*      const std::string& plane); */
  Data(const std::string& fname,
       const std::string& hname,
       const Arguments *args);
  virtual ~Data();
  void Project();
  const std::shared_ptr<TH3> GetH3() const { return h3; };
  std::shared_ptr <TH2> GetH2(const Float_t val) const;
  TAxis *GetNormalAxis() const;
  void SetCentre(Float_t val) { centre=val; }
  Float_t GetCentre() const { return centre; }
};

#endif
