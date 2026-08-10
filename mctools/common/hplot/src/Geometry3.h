#ifndef Geometry3_h_
#define Geometry3_h_

#include "Geometry.h"
#include "Data3.h"

/*!
  Geometry stored as a TH3 of material indices.

  Data3 is inherited privately: it is how a Geometry3 is implemented, not what
  it is - the rest of the program uses the Geometry interface.
*/
class Geometry3 : public Geometry, private Data3 {
 protected:
  virtual void SetH2(std::shared_ptr<TH2> h2) const;
  virtual void BuildMaxH2();

 private:
  mutable std::shared_ptr<TH2> drawn; // the projection currently on the canvas

 public:
  Geometry3(TH3 *h3, const std::shared_ptr<Arguments> args);
  virtual ~Geometry3() = default;

  // needed by the caller to set the geometry up and to check it against the data
  using Data3::Project;
  using Data3::GetNormalAxis;

  std::string GetGOption() const { return "same " + args->GetGoption(); }
  virtual data_t GetType() const { return kGeometry3; }
  virtual std::string GetTypeStr() const { return "Geometry3"; }

  void Draw() override { Draw(Data3::GetOffset()); }
  void Draw(Float_t offset) override;
  std::string StatusText(Double_t x, Double_t y) const override;
};

#endif
