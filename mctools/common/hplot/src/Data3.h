#ifndef Data3_h_
#define Data3_h_

#include <deque>
#include <future>
#include <map>
#include <memory>
#include <string>
#include <vector>

#include <TH3.h>
#include <TH2.h>
#include <TAxis.h>
#include <TGaxis.h>

#include "Arguments.h"
#include "Plane.h"

/*!
  A TH3 and its projections onto the chosen plane.

  One TH2 is produced per bin of the axis normal to the plane; they are built
  on demand by GetH2() and cached, since only one of them is shown at a time.
  Prefetch() builds the ones on both sides of it on worker threads, so that
  moving the slider on usually costs nothing at all.

  The TH3 is not touched after the constructor: -scale, the averaging -rebin
  does and -flip are all folded into the projection instead.  That is faster -
  they were full passes over the TH3, and -flip a copy of it - and it is what
  makes the histogram safe for the worker threads to read.
*/
class Data3 {
 public:
  /// The type ROOT keeps the bin contents of a histogram in
  enum class EKind { F, D, S, I };

 private:
  mutable std::shared_ptr<TGaxis> yrev; // reversed Y axis [if flipped]

  void ErrorHist(std::shared_ptr<TH2> h) const;

  /*!
    Everything one projection needs, as plain numbers and pointers.

    This is all a worker thread is handed, and it makes no ROOT call at all -
    which keeps the threading down to a single rule.  The histograms are made
    by MakeSlice() and dressed by Finish(), both on the main thread.
  */
  struct Job {
    const void *in{nullptr};      ///< bin contents of the TH3
    const Double_t *ein{nullptr}; ///< its sums of squared weights, null if it has none
    void *out{nullptr};           ///< bin contents of the TH2
    Double_t *eout{nullptr};      ///< its sums of squared weights
    Plane::Index i3, i2;          ///< where bin (v,h,n) is in each of them
    Int_t nv{0}, nh{0}, nn{0};    ///< bins along the three directions of the plane
    Int_t nbin{1};                ///< the slice to project, ignored when max
    Double_t scale{1.0};          ///< -scale and the averaging of -rebin
    MaxErr cut;                   ///< -maxerror
    bool max{false};              ///< -max: the largest value along the normal axis
    EKind kind{EKind::F};         ///< element type of both histograms

    /// Project, and return the number of bins written
    Long64_t operator()() const;
  };

  /// The projection loop itself, for one element type
  template <class T> static Long64_t Run(const Job& j);

  /// A projection a worker thread is still busy with
  struct Slice {
    std::shared_ptr<TH2> h2;
    std::shared_future<Long64_t> done;
  };

 protected:
  const std::shared_ptr<Arguments> args;
  Plane plane;
  /*! Read by the worker threads, so not modified after the constructor */
  std::shared_ptr<TH3> h3;
  std::shared_ptr<TH2> h2max;

  EKind kind;      ///< element type of h3, and so of its projections
  Double_t dscale; ///< -scale and the averaging of -rebin, as one factor
  bool flip;       ///< -flip, folded into the vertical bin written

  /// the finished projections, one slot per bin of the normal axis
  mutable std::vector< std::shared_ptr<TH2> > vh2;
  /// the ones a worker thread is still filling in
  mutable std::map<Int_t, Slice> pending;
  /// which slots of vh2 are filled, least recently used first
  mutable std::deque<Int_t> lru;
  size_t maxCached; ///< how many of them may be kept - see Budget()
  /// the slice Prefetch() was last called about, so that it can tell which way
  /// the slider is going
  mutable Int_t lastPrefetch;

  /*! How many projections may be built at once, so that a fast slider does not
      leave a worker thread behind for every slice it went past */
  static constexpr size_t maxPending = 2;
  /*! How much memory the cached projections may take together */
  static constexpr size_t cacheBudget = 256UL << 20;

  Float_t offset; // (initial) normal axis offset - can be changed with MainFrame::slider

  void SetH2(std::shared_ptr<TH2> h2) const;
  void Rebin();
  std::shared_ptr<TH2> MakeH2(std::string& name, std::string& title) const;
  std::shared_ptr<TH2> MakeSlice(Int_t bin) const;
  Job  MakeJob(TH2& h2, Int_t bin) const;
  void Finish(const std::shared_ptr<TH2>& h2, Long64_t entries) const;
  std::shared_ptr<TH2> BuildH2(Int_t bin) const;
  void Launch(Int_t bin) const;
  void Harvest() const;
  void Touch(Int_t bin) const;
  size_t Budget() const;
  Int_t NormalBin(Float_t val) const;
  std::shared_ptr<TH2> Projection(Int_t bin) const;
  Float_t GetOffset(const std::string&) const;

 public:
  /// Read hname from fname
  Data3(const std::string& fname,
	const std::string& hname,
	const std::shared_ptr<Arguments> args);
  /// Take ownership of an already read histogram
  Data3(TH3 *h3,
	const std::shared_ptr<Arguments> args);
  ~Data3();

  /// Read a TH3 out of a ROOT file and detach it from that file
  static TH3 *ReadTH3(const std::string& fname, const std::string& hname);

  void Project();
  /// Start the projections on both sides of the given offset on worker threads
  void Prefetch(Float_t val) const;
  const std::shared_ptr<Arguments> GetArgs() const {return args;}
  std::shared_ptr <TH2> GetH2(const std::string val="") const;
  std::shared_ptr <TH2> GetH2(const Float_t val) const;
  std::shared_ptr<TH2> Draw(const Float_t val) const;
  std::shared_ptr<TH2> Draw(const std::string val="") const;
  void SetOffset(Float_t val) { offset=val; }
  Float_t GetOffset() const { return offset; }
  const Plane& GetPlane() const { return plane; }
  TAxis *GetNormalAxis() const;
  TAxis *GetHorizontalAxis() const;
  TAxis *GetVerticalAxis() const;
  void ReverseYAxis(std::shared_ptr<TH2> h2) const;
};

#endif
