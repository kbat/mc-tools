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
#include "GeometryMultiGraph.h"
#include "Geometry3.h"
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
  std::shared_ptr<Geometry3> geo3;
  std::shared_ptr<GeometryMultiGraph> plotgeom;
  std::shared_ptr<TH2> dh2; // current data histogram
  std::shared_ptr<TH2> gh2; // current geometry histogram

  std::unique_ptr<DynamicSlice> slice;

  void GrabMouseWheel() const;
 public:
  MainFrame(const TGWindow *p, UInt_t w, UInt_t h,
	    const std::shared_ptr<Data3> data);
  virtual ~MainFrame();

  void SetGeometry(const std::shared_ptr<Geometry3>);
  void SetGeometry(const std::shared_ptr<GeometryMultiGraph>);

  TCanvas *GetCanvas() const { return fEcanvas->GetCanvas(); }
  TVirtualPad *GetHistogramPad() const;
  TVirtualPad *GetSlicePad() const;
  void DoSlider();
  Bool_t ProcessMessage(Long_t msg, Long_t parm1, Long_t parm2) override;

  void EventInfo(EEventType event, Int_t px, Int_t py, TObject *selected);
  Bool_t HandleButton(Event_t *event) override;

  ClassDef(MainFrame,0);
};

#endif
