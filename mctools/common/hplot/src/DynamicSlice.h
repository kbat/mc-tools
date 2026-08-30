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

  /*!
    What DrawSlice() last projected, and from what.

    Re-projecting shows nothing new until the cursor crosses into another bin,
    so these say when it may be skipped.  The histogram belongs in there as
    well as the bin: the slider replaces it without the bin number changing,
    and the slice pad would otherwise keep showing the previous slice.  dirty
    covers everything else that invalidates the picture - the axis swap and the
    log scale below.
  */
  Int_t lastbin;
  const TH2 *lasth2;
  bool dirty;

  std::pair<double, double> DrawSlice(const std::shared_ptr<TH2>, const Double_t, const std::string&);
 public:
  DynamicSlice(size_t nbins, size_t ngroup);
  void Draw(const std::shared_ptr<TH2> h2, TVirtualPad *h2pad, TVirtualPad *slicePad);
};

#endif
