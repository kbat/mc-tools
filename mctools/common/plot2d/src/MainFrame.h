#ifndef MainFrame_h_
#define MainFrame_h_

#include <TGFrame.h>
#include <TRootEmbeddedCanvas.h>

class MainFrame : public TGMainFrame {
 private:
  TRootEmbeddedCanvas *fEcanvas;
 public:
  MainFrame(const TGWindow *p,UInt_t w,UInt_t h);
  virtual ~MainFrame() { Cleanup();  }
  void DoDraw();
  ClassDef(MainFrame,0);
};

#endif
