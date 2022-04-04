#ifndef Profile_h_
#define Profile_h_

#include <TVirtualX.h>
#include <TH2.h>
#include "Data3.h"

class Profile {
  std::shared_ptr<TH2> h2;
  std::shared_ptr<Data3> data;
  std::shared_ptr<TH1F> hprofile;
  bool logy;
  TVirtualPad *pad; // pad with slice

  void DrawProfile(const std::shared_ptr<TH2>, const Int_t, const Int_t);
 public:
  Profile(const std::shared_ptr<Data3>);
  void Draw(const std::shared_ptr<TH2> h2, TVirtualPad *h2pad, TVirtualPad *slicePad);
};

#endif
