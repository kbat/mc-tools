#ifndef Data3_h_
#define Data3_h_

#include <memory>
#include <string>
#include <vector>

#include <TH3.h>
#include <TH2.h>
#include <TAxis.h>
#include <TGaxis.h>

#include "Arguments.h"
#include "Plane.h"

enum data_t {kData3, kGeometry3};

/*!
  A TH3 and its projections onto the chosen plane.

  One TH2 is produced per bin of the axis normal to the plane; they are built
  on demand by GetH2() and cached, since only one of them is shown at a time.
*/
class Data3 {
 private:
  mutable std::shared_ptr<TGaxis> yrev; // reversed Y axis [if flipped]

  void Flip();
  void ErrorHist(std::shared_ptr<TH2> h) const;

 protected:
  const std::shared_ptr<Arguments> args;
  Plane plane;
  std::shared_ptr<TH3> h3;
  std::shared_ptr<TH2> h2max;
  mutable std::vector< std::shared_ptr<TH2> > vh2;
  Float_t offset; // (initial) normal axis offset - can be changed with MainFrame::slider

  virtual void SetH2(std::shared_ptr<TH2> h2) const;
  void Rebin();
  std::shared_ptr<TH2> MakeH2(std::string& name, std::string& title) const;
  std::shared_ptr<TH2> BuildH2(Int_t bin) const;
  virtual void BuildMaxH2();
  Float_t GetOffset(const std::string&) const;

 public:
  /// Read hname from fname
  Data3(const std::string& fname,
	const std::string& hname,
	const std::shared_ptr<Arguments> args);
  /// Take ownership of an already read histogram
  Data3(TH3 *h3,
	const std::shared_ptr<Arguments> args);
  virtual ~Data3() = default;

  /// Read a TH3 out of a ROOT file and detach it from that file
  static TH3 *ReadTH3(const std::string& fname, const std::string& hname);

  void Project();
  const std::shared_ptr<Arguments> GetArgs() const {return args;}
  const std::shared_ptr<TH3> GetH3() const { return h3; };
  std::shared_ptr <TH2> GetH2(const std::string val="") const;
  std::shared_ptr <TH2> GetH2(const Float_t val) const;
  virtual std::shared_ptr<TH2> Draw(const Float_t val) const;
  virtual std::shared_ptr<TH2> Draw(const std::string val="") const;
  void SetOffset(Float_t val) { offset=val; }
  Float_t GetOffset() const { return offset; }
  const Plane& GetPlane() const { return plane; }
  TAxis *GetNormalAxis() const;
  TAxis *GetHorizontalAxis() const;
  TAxis *GetVerticalAxis() const;
  Bool_t Check(TAxis *normal) const;
  virtual data_t GetType() const { return kData3; }
  virtual std::string GetTypeStr() const { return "Data3"; }
  void ReverseYAxis(std::shared_ptr<TH2> h2) const;
};

#endif
