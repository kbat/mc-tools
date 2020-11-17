#ifndef Data_h_
#define Data_h_

#include <chrono>

#include <TH3.h>
#include <TH2.h>
#include <TAxis.h>

#include "Arguments.h"

enum data_t {kData, kGeometry};

class Data {
 private:
  std::shared_ptr<TH3> h3;
  std::string plane;

  TAxis *GetHorizontalAxis() const;
  TAxis *GetVerticalAxis() const;
  char   GetNormalAxisName() const;
  Float_t GetOffset(const std::string&) const;
  void Flip();
  void ErrorHist(std::shared_ptr<TH2> h) const;
 protected:
  std::vector< std::shared_ptr<TH2> > vh2;
  const Arguments *args;
  Float_t offset; // (initial) normal axis offset - can be changed with MainFrame::slider
  virtual void SetH2(std::shared_ptr<TH2> h2);
  void Rebin() const;
 public:
  /* Data(const TH3F* h3, */
  /*      const std::string& plane); */
  Data(const std::string& fname,
       const std::string& hname,
       const Arguments *args);
  virtual ~Data();
  void Project();
  const std::shared_ptr<TH3> GetH3() const { return h3; };
  std::shared_ptr <TH2> GetH2(const std::string val) const;
  std::shared_ptr <TH2> GetH2(const Float_t val) const;
  virtual void Draw(const Float_t val) const;
  virtual void Draw(const std::string val="") const;
  void SetOffset(Float_t val) { offset=val; }
  Float_t GetOffset() const { return offset; }
  TAxis *GetNormalAxis() const;
  Bool_t Check(TAxis *normal) const;
  virtual data_t GetType() const { return kData; }
  virtual std::string GetTypeStr() const { return "Data"; }
  void PrintChrono(std::chrono::system_clock::time_point start, std::string msg) const;
  void ReverseYAxis(std::shared_ptr<TH2> h2) const;
};

#endif
