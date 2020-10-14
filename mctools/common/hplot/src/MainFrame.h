#ifndef MainFrame_h_
#define MainFrame_h_

#include <TGFrame.h>
#include <TRootEmbeddedCanvas.h>
#include <TGLayout.h>
#include <TGMenu.h>
#include <TGDoubleSlider.h>


class MainFrame : public TGMainFrame {
 private:
  TRootEmbeddedCanvas *fEcanvas;
  TGMenuBar           *fMenuBar;
  TGPopupMenu         *fMenuFile;
  TGDoubleVSlider     *fSlider;
 public:
  MainFrame(const TGWindow *p,UInt_t w,UInt_t h);
  virtual ~MainFrame();
  void DoDraw();
  TCanvas *GetCanvas() const { return fEcanvas->GetCanvas(); }
  Bool_t ProcessMessage(Long_t msg, Long_t parm1, Long_t parm2);
  ClassDef(MainFrame,0);
};

#endif
