#ifndef Data3_h_
#define Data3_h_

#include <TH3.h>
#include <TH2.h>
#include <TAxis.h>
#include <TGaxis.h>

#include "Data.h"
#include "Arguments.h"

enum data_t {kData3, kGeometry};

class Data3 : public Data {
 private:
  mutable std::shared_ptr<TGaxis> yrev; // reversed Y axis [if flipped]

  TAxis *GetHorizontalAxis() const;
  TAxis *GetVerticalAxis() const;
  char   GetNormalAxisName() const;
  void Flip();
  void ErrorHist(std::shared_ptr<TH2> h) const;
 protected:
  std::string plane;
  std::shared_ptr<TH3> h3;
  std::shared_ptr<TH2> h2max;
  std::vector< std::shared_ptr<TH2> > vh2;
  Float_t offset; // (initial) normal axis offset - can be changed with MainFrame::slider
  virtual void SetH2(std::shared_ptr<TH2> h2);
  void Rebin() const;
  std::shared_ptr<TH2> MakeH2(std::string& name, std::string& title);
  virtual void BuildMaxH2();
  Float_t GetOffset(const std::string&) const;
 public:
  /* Data3(const TH3F* h3, */
  /*      const std::string& plane); */
  Data3(const std::string& fname,
	const std::string& hname,
	const std::shared_ptr<Arguments> args);
  virtual ~Data3();
  void Project();
  const std::shared_ptr<Arguments> GetArgs() const {return args;}
  const std::shared_ptr<TH3> GetH3() const { return h3; };
  std::shared_ptr <TH2> GetH2(const std::string val="") const;
  std::shared_ptr <TH2> GetH2(const Float_t val) const;
  virtual std::shared_ptr<TH2> Draw(const Float_t val) const;
  virtual std::shared_ptr<TH2> Draw(const std::string val="") const;
  void SetOffset(Float_t val) { offset=val; }
  Float_t GetOffset() const { return offset; }
  TAxis *GetNormalAxis() const;
  Bool_t Check(TAxis *normal) const;
  virtual data_t GetType() const { return kData3; }
  virtual std::string GetTypeStr() const { return "Data3"; }
  const std::vector<std::shared_ptr<TH2> > GetVH2() const {return vh2;}
  void ReverseYAxis(std::shared_ptr<TH2> h2) const;
};

#endif
