#ifndef DynamicSlice_h_
#define DynamicSlice_h_

#include <TVirtualX.h>
#include <TH2.h>

class DynamicSlice {
  const size_t nbins;
  const size_t ngroup;
  bool projection;
  bool logy;
  std::pair<double, double> range;
  std::pair<int, int> old;
  TVirtualPad *pad; // pad with slice

  std::pair<double, double> DrawSlice(const std::shared_ptr<TH2>, const Double_t, const std::string&);
 public:
  DynamicSlice(size_t nbins, size_t ngroup);
  void Draw(const std::shared_ptr<TH2> h2, TVirtualPad *h2pad, TVirtualPad *slicePad);
};

#endif
