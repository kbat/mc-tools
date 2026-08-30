#ifndef MainFrame_h_
#define MainFrame_h_

#include <TGFrame.h>
#include <TRootEmbeddedCanvas.h>
#include <TGLayout.h>
#include <TGMenu.h>
#include <TGSlider.h>
#include <TGStatusBar.h>
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

  std::shared_ptr<Data3> data;
  std::shared_ptr<Geometry> geo;
  std::shared_ptr<TH2> dh2; // current data histogram

  std::unique_ptr<DynamicSlice> slice;

  void GrabMouseWheel() const;

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
  void CloseWindow() override;
  Bool_t ProcessMessage(Long_t msg, Long_t parm1, Long_t parm2) override;

  void EventInfo(EEventType event, Int_t px, Int_t py, TObject *selected);
  Bool_t HandleButton(Event_t *event) override;

  ClassDefOverride(MainFrame,0);
};

#endif
