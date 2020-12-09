#ifndef DynamicSlice_h_
#define DynamicSlice_h_

#include <TVirtualX.h>
#include <TH2.h>

class DynamicSlice {
  std::shared_ptr<TH2> h2;
  const size_t nbins;
  const size_t ngroup;
  bool projection;
  bool logy;
  std::pair<double, double> range;
  std::pair<int, int> old;
  TVirtualPad *cX;
  TVirtualPad *cY;
 public:
  DynamicSlice(const std::vector<unsigned short>&);
  void DestroyPrimitive(const std::string&);
  void call(const std::shared_ptr<TH2> h2);
  std::pair<double, double> DrawSlice(const std::shared_ptr<TH2>, const Int_t, const std::string&);
};

#endif
