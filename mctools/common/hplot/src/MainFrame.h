#ifndef MainFrame_h_
#define MainFrame_h_

#include <TGFrame.h>
#include <TRootEmbeddedCanvas.h>
#include <TGLayout.h>
#include <TGMenu.h>
#include <TGSlider.h>
#include <TGStatusBar.h>
#include <TTimer.h>
#include <Buttons.h>
#include <TVirtualPad.h>

#include "Data3.h"
#include "Geometry.h"
#include "DynamicSlice.h"

class MainFrame : public TGMainFrame {
 private:
  TRootEmbeddedCanvas *fEcanvas;
  TGMenuBar           *fMenuBar;
  TGPopupMenu         *fMenuFile;
  TGPopupMenu         *fMenuHelp;
  TGVSlider           *fSlider;
  TGStatusBar         *fStatusBar;
  TTimer              *fRangeTimer;

  std::shared_ptr<Data3> data;
  std::shared_ptr<Geometry> geo;
  std::shared_ptr<TH2> dh2; // current data histogram

  std::unique_ptr<DynamicSlice> slice;

  /*!
    Where the pointer was when the status bar was last written, and which bin
    of the data histogram it was over.

    EventInfo() runs on every motion event, so it recomputes only what these
    say can have changed.  Both are reset by ShowH2Name() when another slice is
    drawn: the value shown belongs to the histogram it was read from, not to
    the bin number alone.
  */
  std::pair<Int_t,Int_t> lastpixel;
  std::pair<Int_t,Int_t> lastbin;

  /// The rectangle the plot axes show, in their own coordinates
  struct Range {
    Double_t hmin{0.0}, hmax{0.0}, vmin{0.0}, vmax{0.0};
    Bool_t Same(const Range& r) const;
  };

  /*!
    What the axes showed when the geometry was last cut, and whether that has
    been seen at all yet - the pad has no user range before it is first
    painted, which is after this window is built.

    The user may zoom the plot with the mouse at any time, and the geometry is
    cut over the rectangle that was on the screen rather than read from a file,
    so the outlines only stay as precise as the picture if they are cut again
    for the new one.  CheckRange() compares these numbers with the pad a few
    times a second: no signal covers every way the range can change - the box
    zoom, an axis dragged, a double click, the axis context menu - and a timer
    also keeps the recut out of the painting it would otherwise happen inside.
  */
  Range fGeoRange;
  Bool_t fGeoRangeSet;
  Bool_t fInCheckRange; ///< CheckRange() calls Update(), which may come back

  void GrabMouseWheel() const;
  void ShowH2Name();
  Bool_t OnHistogramPad(Int_t px, Int_t py) const;
  Bool_t OnHistogramFrame(Int_t px, Int_t py) const;

  /*!
    TGVSlider is an integer widget whose positions count downwards - the
    smallest one at the top.  Neither suits the axis normal to the projection
    plane, which is a float coordinate in cm that SetRange()/SetPosition()
    would silently truncate (an axis spanning less than a couple of cm would
    collapse onto a single position), and whose value the user expects to grow
    as the knob goes up.

    So the slider is run in bin numbers counted from the top: bin b sits at
    position nbins+1-b.  One notch of the wheel is then exactly one bin,
    nothing is lost to truncation, and the knob moves the way the coordinate
    does.
  */
  Int_t    CoordToSlider(Double_t x) const;
  Double_t SliderToCoord(Int_t pos) const;
 public:
  MainFrame(const TGWindow *p, UInt_t w, UInt_t h,
	    const std::shared_ptr<Data3> data);
  virtual ~MainFrame();

  void SetGeometry(const std::shared_ptr<Geometry>);

  TCanvas *GetCanvas() const { return fEcanvas->GetCanvas(); }
  TVirtualPad *GetHistogramPad() const;
  TVirtualPad *GetSlicePad() const;
  void DoSlider();
  /// Re-cut and redraw the geometry if the plotted range has changed
  void CheckRange();
  void CloseWindow() override;
  Bool_t ProcessMessage(Long_t msg, Long_t parm1, Long_t parm2) override;

  void EventInfo(EEventType event, Int_t px, Int_t py, TObject *selected);
  Bool_t HandleButton(Event_t *event) override;

  ClassDefOverride(MainFrame,0);
};

#endif
