#ifndef MainFrame_h_
#define MainFrame_h_

#include <TGFrame.h>
#include <TRootEmbeddedCanvas.h>
#include <TGLayout.h>
#include <TGMenu.h>

class MainFrame : public TGMainFrame {
 private:
  TRootEmbeddedCanvas *fEcanvas;
  TGLayoutHints       *fMenuBarLayout;
  TGLayoutHints       *fMenuBarItemLayout;
  TGMenuBar           *fMenuBar;
  TGPopupMenu         *fMenuFile;
 public:
  MainFrame(const TGWindow *p,UInt_t w,UInt_t h);
  virtual ~MainFrame() { Cleanup();  }
  void DoDraw();
  TCanvas *GetCanvas() const { return fEcanvas->GetCanvas(); }
  ClassDef(MainFrame,0);
};

#endif
