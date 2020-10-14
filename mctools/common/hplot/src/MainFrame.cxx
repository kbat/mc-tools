#include <TApplication.h>
#include <TGClient.h>
#include <TCanvas.h>
#include <TF1.h>
#include <TRandom.h>
#include <TGButton.h>
#include <TRootEmbeddedCanvas.h>
#include "MainFrame.h"

enum ETextEditorCommands {kM_FILE_NEW};

MainFrame::MainFrame(const TGWindow *p,UInt_t w,UInt_t h)
  : TGMainFrame(p,w,h)
{

  // Menu bar
  fMenuBarLayout = new TGLayoutHints(kLHintsTop | kLHintsExpandX, 0, 0, 1, 1);
  fMenuBar = new TGMenuBar(this, 1, 1, kHorizontalFrame);

  fMenuBarItemLayout = new TGLayoutHints(kLHintsTop | kLHintsLeft, 0, 4, 0, 0);
  fMenuFile = new TGPopupMenu(fClient->GetRoot());
  fMenuFile->AddEntry(" &New", kM_FILE_NEW, 0,
		      gClient->GetPicture("ed_new.png"));

  fMenuFile->Associate(this);

  fMenuBar->AddPopup("&File", fMenuFile, fMenuBarItemLayout);

  AddFrame(fMenuBar, fMenuBarLayout);

  // Creates widgets of the example
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
