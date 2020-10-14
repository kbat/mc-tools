#include <TApplication.h>
#include <TGClient.h>
#include <TCanvas.h>
#include <TF1.h>
#include <TRandom.h>
#include <TGButton.h>
#include <TRootEmbeddedCanvas.h>
#include "MainFrame.h"

enum MainFrameMessageTypes {
			    M_FILE_SAVEAS,
			    M_FILE_EXIT
};

MainFrame::MainFrame(const TGWindow *p,UInt_t w,UInt_t h)
  : TGMainFrame(p,w,h)
{

  // Menu bar
  fMenuBar = new TGMenuBar(this, 1, 1, kHorizontalFrame);

  fMenuFile = new TGPopupMenu(fClient->GetRoot());
  fMenuFile->AddEntry("S&ave as...\tCtrl+A", M_FILE_SAVEAS);
  fMenuFile->DisableEntry(M_FILE_SAVEAS);
  fMenuFile->AddEntry("E&xit\tCtrl+Q", M_FILE_EXIT, 0, gClient->GetPicture("bld_exit.png"));
  fMenuFile->Associate(this);

  fMenuBar->AddPopup("&File", fMenuFile,
		     new TGLayoutHints(kLHintsTop | kLHintsLeft, 0, 4, 0, 0));

  AddFrame(fMenuBar,
	   new TGLayoutHints(kLHintsTop | kLHintsExpandX, 0, 0, 1, 1));

  // Canvas
  fEcanvas = new TRootEmbeddedCanvas ("Ecanvas",this,w,h);
  AddFrame(fEcanvas, new TGLayoutHints(kLHintsExpandX |
				       kLHintsExpandY, 10,10,10,1));
  TGHorizontalFrame *hframe=new TGHorizontalFrame(this, w,40);
  TGTextButton *draw = new TGTextButton(hframe,"&Draw");
  draw->Connect("Clicked()","MainFrame",this,"DoDraw()");
  hframe->AddFrame(draw, new TGLayoutHints(kLHintsCenterX,
					   5,5,3,4));
  TGTextButton *exit = new TGTextButton(hframe,"&Exit ",
					"gApplication->Terminate()");
  hframe->AddFrame(exit, new TGLayoutHints(kLHintsCenterX,
					   5,5,3,4));
  AddFrame(hframe,new TGLayoutHints(kLHintsCenterX,2,2,2,2));

  //////////

  MapSubwindows();
  Resize(GetDefaultSize());
  MapWindow();

  fEcanvas->Connect("TCanvas", "Closed()", "TApplication", gApplication, "Terminate()");
}

void MainFrame::DoDraw()
{
  TF1 *f1 = new TF1("f1","sin(x)/x",0,gRandom->Rndm()*10);
  f1->SetLineWidth(3);
  f1->Draw();
  TCanvas *fCanvas = GetCanvas();
  fCanvas->cd();
  fCanvas->Update();
}

MainFrame::~MainFrame()
{
  // .help TGMainFrame::Cleanup
  // Cleanup and delete all objects contained in this composite frame.
  // This will delete all objects added via AddFrame().
  Cleanup();
}

Bool_t MainFrame::ProcessMessage(Long_t msg, Long_t parm1, Long_t parm2)
{
  // Window_t wdummy;
  //  int ax, ay;
   // TRootHelpDialog *hd;
   // TGListTreeItem *item;
   // TGFileInfo fi;
   // Char_t  strtmp[250];

  // std::cout << "here: " << msg << " " << parm1 << " " << parm2 << "\t" << M_FILE_EXIT << std::endl;
  // std::cout << "\t" << GET_MSG(msg) << " " << GET_SUBMSG(msg) << std::endl;
  // std::cout << "\t" << kC_COMMAND << " " << kCM_MENU << std::endl;

  switch (GET_MSG(msg)) {
  case kC_COMMAND:
    switch (GET_SUBMSG(msg)) {
    case M_FILE_EXIT:
      std::cout << "file -> exit" << std::endl;
      gApplication->Terminate();
      break;
    default:
      break;
    }
  default:
    break;
  }
  return kTRUE;
}
