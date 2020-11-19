#include <TApplication.h>
#include <TGClient.h>
#include <TCanvas.h>
#include <TF1.h>
#include <TRandom.h>
#include <TGButton.h>
#include <TRootEmbeddedCanvas.h>
#include <TAxis.h>

#include "MainFrame.h"

enum MainFrameMessageTypes {
			    M_FILE_SAVEAS,
			    M_FILE_EXIT,
			    M_HELP_ABOUT
};

MainFrame::MainFrame(const TGWindow *p, UInt_t w, UInt_t h,
		     const std::shared_ptr<Data> data,
		     const std::shared_ptr<Geometry> geo) :
  TGMainFrame(p,w,h), data(data), geo(geo)
{

  // Menu bar
  fMenuBar = new TGMenuBar(this, 1, 1, kHorizontalFrame);

  // File
  fMenuFile = new TGPopupMenu(fClient->GetRoot());
  fMenuFile->AddEntry("S&ave as...\tCtrl+A", M_FILE_SAVEAS);
  fMenuFile->DisableEntry(M_FILE_SAVEAS);
  fMenuFile->AddEntry("E&xit\tCtrl+Q", M_FILE_EXIT, 0, gClient->GetPicture("bld_exit.png"));
  fMenuFile->Associate(this);

  fMenuBar->AddPopup("&File", fMenuFile,
		     new TGLayoutHints(kLHintsTop | kLHintsLeft, 0, 4, 0, 0));

  // Help
  fMenuHelp = new TGPopupMenu(fClient->GetRoot());
  fMenuHelp->AddEntry("About", M_HELP_ABOUT, 0, gClient->GetPicture("about.xpm"));
  fMenuHelp->Associate(this);

  fMenuBar->AddPopup("&Help", fMenuHelp,
		     new TGLayoutHints(kLHintsTop | kLHintsRight, 0, 4, 0, 0));

  AddFrame(fMenuBar,
	   new TGLayoutHints(kLHintsTop | kLHintsExpandX, 0, 0, 1, 1));

  TGHorizontalFrame *hframe=new TGHorizontalFrame(this, w,h);

  // Canvas
  fEcanvas = new TRootEmbeddedCanvas ("Ecanvas",hframe,w,h);
  // AddFrame(fEcanvas, new TGLayoutHints(kLHintsLeft | kLHintsExpandX | kLHintsExpandY, 10,10,10,1));

  TCanvas *c1 = fEcanvas->GetCanvas();
  c1->Connect("ProcessedEvent(Int_t,Int_t,Int_t,TObject*)","MainFrame",this,
	      "EventInfo(EEventType,Int_t,Int_t,TObject*)");


  hframe->AddFrame(fEcanvas, new TGLayoutHints(kLHintsLeft | kLHintsExpandX |
				       kLHintsExpandY, 10,10,10,1));

  const TAxis *a  = data->GetNormalAxis();
  const Int_t nbins = a->GetNbins();

  if (nbins>1)
    {
      Int_t bin = a->FindBin(data->GetOffset());
      if (bin > nbins)
	bin = nbins;
      else if (bin==0)
	bin = 1;

      fSlider = new TGDoubleVSlider(hframe,
				    20, // slider width
				    kDoubleScaleBoth, // slider type [1 or 2]
				    -1,
				    kVerticalFrame,
				    GetDefaultFrameBackground(),
				    kTRUE,kTRUE);
      fSlider->SetRange(a->GetXmin(), a->GetXmax());
      fSlider->SetPosition(a->GetBinLowEdge(bin), a->GetBinUpEdge(bin));
      fSlider->SetScale(1000.0/nbins);
      hframe->AddFrame(fSlider,new TGLayoutHints(kLHintsRight | kLHintsExpandY, 10,10,10,1));
      //      fSlider->Connect("PositionChanged()", "MainFrame", this, "DoSlider()");
      fSlider->Connect("Released()", "MainFrame", this, "DoSlider()");
    }

  AddFrame(hframe,new TGLayoutHints(kLHintsCenterX|kLHintsExpandX|kLHintsExpandY,2,2,2,2));

  // Status bar
  const Int_t nparts = 4;
  std::array<Int_t,4> parts = {45, 15, 10, 30};
  fStatusBar = new TGStatusBar(this, 50, 10, kVerticalFrame);
  fStatusBar->SetParts(parts.data(), nparts);
  fStatusBar->Draw3DCorner(kTRUE);
  AddFrame(fStatusBar, new TGLayoutHints(kLHintsExpandX, 0, 0, 10, 0));

  // TGHorizontalFrame *hframe1=new TGHorizontalFrame(this, w,40);
  // TGTextButton *draw = new TGTextButton(hframe1,"&Draw");
  // draw->Connect("Clicked()","MainFrame",this,"DoDraw()");
  // hframe1->AddFrame(draw, new TGLayoutHints(kLHintsCenterX,
  // 					   5,5,3,4));

  // TGTextButton *exit = new TGTextButton(hframe1,"&Exit ",
  // 					"gApplication->Terminate()");
  // exit->SetState(kButtonDisabled);
  // hframe1->AddFrame(exit, new TGLayoutHints(kLHintsCenterX,
  // 					   5,5,3,4));
  // AddFrame(hframe1,new TGLayoutHints(kLHintsCenterX,2,2,2,2));

  //////////

  MapSubwindows();
  Resize(GetDefaultSize());
  MapWindow();

  fEcanvas->Connect("TCanvas", "Closed()", "TApplication", gApplication, "Terminate()");

  h2 = data->GetH2(); // default histogram
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

void MainFrame::DoSlider()
{
  float ymin, ymax;
  fSlider->GetPosition(ymin,ymax);
  const float y = (ymin+ymax)/2.0;

  //  std::cout << data->GetH2(y)->GetTitle() << std::endl;;
  GetCanvas()->cd();
  h2 = data->Draw(y);
  //  data->GetH2(y)->Draw();

  if (geo)
    geo->Draw(y);

  GetCanvas()->Update();
}

Bool_t MainFrame::ProcessMessage(Long_t msg, Long_t parm1, Long_t parm2)
{
  // Window_t wdummy;
  //  int ax, ay;
   // TRootHelpDialog *hd;
   // TGListTreeItem *item;
   // TGFileInfo fi;
   // Char_t  strtmp[250];

  std::cout << "Process: " << msg << " " << parm1 << " " << parm2 << std::endl;
  std::cout << "\t" << GET_MSG(msg) << " " << GET_SUBMSG(msg) << std::endl;
  std::cout << "\t" << kC_COMMAND << " " << kCM_MENU << std::endl;

  switch (GET_MSG(msg)) {
  case kC_COMMAND:
    switch (GET_SUBMSG(msg)) {
    case M_FILE_EXIT:
      std::cout << "file -> exit" << std::endl;
      gApplication->Terminate();
      break;
    case M_HELP_ABOUT:
      std::cout << "Help" << std::endl;
      break;

    default:
      break;
    }
  default:
    break;
  }
  return kTRUE;
}

void MainFrame::EventInfo(EEventType event, Int_t px, Int_t py, TObject *selected)
{
//  Writes the event status in the status bar parts

   fStatusBar->SetText(h2->GetTitle(),0);
   fStatusBar->SetText(h2->GetName(),1);

   char text2[50];
   if (event == kKeyPress)
     sprintf(text2, "%c %c", (char) px, (char) py);
   else
      sprintf(text2, "%d,%d", px, py);

   fStatusBar->SetText(text2,2);

   // value and error
   const Double_t x  = gPad->PadtoX(gPad->AbsPixeltoX(px));
   const Double_t y  = gPad->PadtoY(gPad->AbsPixeltoY(py));

   const Int_t binx = h2->GetXaxis()->FindFixBin(x);
   const Int_t biny = h2->GetYaxis()->FindFixBin(y);

   const Double_t val = h2->GetBinContent(binx, biny);
   const Double_t err = h2->GetBinError(binx, biny);
   Double_t relerr = 100.0;
   if (std::abs(val)>0)
     relerr = err/val * 100.0;

   fStatusBar->SetText(Form("%g +- %.0f %%", val,relerr),3);
}
