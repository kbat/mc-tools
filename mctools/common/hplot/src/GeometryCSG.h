#ifndef GeometryCSG_h_
#define GeometryCSG_h_

#include <deque>
#include <future>
#include <map>
#include <memory>
#include <string>
#include <vector>

#include <TMultiGraph.h>

#include "Arguments.h"
#include "CSGEngine.h"
#include "Data3.h"
#include "Geometry.h"

/*!
  The geometry of a Monte Carlo input file, cut by the plane the data are
  projected on and drawn as the outlines of its material boundaries.

  The cut is made by hplot itself (CSGEngine), so it follows the data: the same
  projection plane, the same range along both axes, and the same offset along
  the normal axis, which means the outlines still match after the slider is
  moved.  Nothing is read from a file prepared in advance.

  Cutting takes a noticeable fraction of a second, so the offsets that have
  been asked for are kept - as many of them as fit the cache budget - and
  Prefetch() starts the next ones on worker threads before they are needed:
  during the projection of the data at start-up, and ahead of the slider
  afterwards.
*/
class GeometryCSG : public Geometry {
 private:
  const std::shared_ptr<Arguments> args;
  const std::shared_ptr<Data3> data;

  CSGEngine engine;
  std::string tmpfile; ///< set if the input file was extracted from a TMacro

  CSGCut cut; ///< the cut with everything but the offset filled in

  /// A finished cut, and roughly what it costs to keep - see Size()
  struct Cut {
    std::shared_ptr<TMultiGraph> mg;
    size_t bytes{0};
  };

  /// the cuts being computed, and the ones already turned into a TMultiGraph
  mutable std::map<Double_t, std::shared_future<std::vector<CSGPolyline> > > pending;
  mutable std::map<Double_t, Cut> cache;
  /// which offsets the cache holds, least recently used first
  mutable std::deque<Double_t> lru;
  mutable size_t cached; ///< how much memory they take together

  std::shared_ptr<TMultiGraph> drawn; ///< the outlines currently on the canvas
  Double_t drawnOffset; ///< where the outlines on the canvas were cut
  Int_t drawnBin;       ///< which bin of the normal axis that offset is in

  /// How many cuts may be running at once, so that a fast slider does not
  /// leave a worker thread behind for every slice it went past
  static constexpr size_t maxPending = 2;
  /*! How much memory the cached cuts may take together, and how many are kept
      whatever their size: the one on the canvas, and the ones Prefetch() is
      working towards on either side of it */
  static constexpr size_t cacheBudget = 64UL << 20;
  static constexpr size_t minCached = 5;

  std::string InputFile();
  void SetUpCut();
  void Harvest() const;
  static size_t Size(const TMultiGraph& mg);
  void Store(Double_t offset, const std::shared_ptr<TMultiGraph>& mg) const;
  void Touch(Double_t offset) const;
  Double_t CutOffset(Float_t offset) const;
  Double_t FlipOffset() const;
  std::shared_ptr<TMultiGraph> GetMultiGraph(Double_t offset) const;
  std::shared_ptr<TMultiGraph> MakeMultiGraph(const std::vector<CSGPolyline>& p) const;

 public:
  GeometryCSG(const std::shared_ptr<Arguments> args,
	      const std::shared_ptr<Data3> data);
  virtual ~GeometryCSG();

  /// Start cutting at the given offset on a worker thread, if not done already
  void Prefetch(Float_t offset) const;

  void Draw() override { Draw(data->GetOffset()); }
  void Draw(Float_t offset) override;
  void Pop() override { if (drawn) drawn->Pop(); }
  std::string StatusText(Double_t x, Double_t y) const override;
};

#endif
