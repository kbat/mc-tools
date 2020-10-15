#ifndef MainFrame_h_
#define MainFrame_h_

#include <TGFrame.h>
#include <TRootEmbeddedCanvas.h>
#include <TGLayout.h>
#include <TGMenu.h>
#include <TGDoubleSlider.h>

#include "Data.h"
#include "Geometry.h"


class MainFrame : public TGMainFrame {
 private:
  TRootEmbeddedCanvas *fEcanvas;
  TGMenuBar           *fMenuBar;
  TGPopupMenu         *fMenuFile;
  TGDoubleVSlider     *fSlider;

  std::shared_ptr<Data> data;
  std::shared_ptr<Geometry> geo;
 public:
  MainFrame(const TGWindow *p, UInt_t w, UInt_t h,
	    const std::shared_ptr<Data> data,
	    const std::shared_ptr<Geometry> geo);
  virtual ~MainFrame();
  void DoDraw();
  TCanvas *GetCanvas() const { return fEcanvas->GetCanvas(); }
  void DoSlider();
  Bool_t ProcessMessage(Long_t msg, Long_t parm1, Long_t parm2);

  ClassDef(MainFrame,0);
};

#endif
