#include <TApplication.h>
#include <TGClient.h>
#include <TCanvas.h>
#include <TF1.h>
#include <TRandom.h>
#include <TGButton.h>
#include <TRootEmbeddedCanvas.h>
#include <TAxis.h>

#include "MainFrame.h"

#include <iomanip>

enum MainFrameMessageTypes {
  M_FILE_SAVEAS,
  M_FILE_EXIT,
  M_HELP_ABOUT
};

const char line_width = getenv("COLUMNS") ? atoi(getenv("COLUMNS"))-1 : 80-1;
const std::string spaces{line_width, ' '};

MainFrame::MainFrame(const TGWindow *p, UInt_t w, UInt_t h,
		     const std::shared_ptr<Data3> data) :
  TGMainFrame(p,w,h), fSlider(nullptr), data(data), geo3(nullptr), plotgeom(nullptr), gh2(nullptr), slice(nullptr)
{
  GrabMouseWheel();

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

  TCanvas *c1 = GetCanvas();
  c1->Connect("ProcessedEvent(Int_t,Int_t,Int_t,TObject*)","MainFrame",this,
	      "EventInfo(EEventType,Int_t,Int_t,TObject*)");

  hframe->AddFrame(fEcanvas, new TGLayoutHints(kLHintsLeft | kLHintsExpandX |
				       kLHintsExpandY, 10,10,10,1));

  if (data->GetVH2().size()>1)
    {
      const TAxis *a  = data->GetNormalAxis();
      const Int_t nbins = a->GetNbins();

      Int_t bin = a->FindBin(data->GetOffset());
      if (bin > nbins)
	bin = nbins;
      else if (bin==0)
	bin = 1;

      fSlider = new TGVSlider(hframe, 40, kSlider1 | kScaleBoth);
      fSlider->Associate(this);
      fSlider->SetRange(a->GetXmin(), a->GetXmax());
      fSlider->SetPosition(a->GetBinCenter(bin));
      fSlider->SetScale(1000.0/nbins);
      hframe->AddFrame(fSlider,new TGLayoutHints(kLHintsBottom | kLHintsExpandY, 10,10,10,1));
      //      fSlider->Connect("Released()", "MainFrame", this, "DoSlider()");
      //      fSlider->SetObject(this);
    }

  AddFrame(hframe,new TGLayoutHints(kLHintsCenterX|kLHintsExpandX|kLHintsExpandY,2,2,2,2));

  // Status bar
  const Int_t nparts = 4;
  std::array<Int_t,4> parts = {45, 15, 10, 30};
  fStatusBar = new TGStatusBar(this, 50, 10, kVerticalFrame);
  fStatusBar->SetParts(parts.data(), nparts);
  fStatusBar->Draw3DCorner(kTRUE);
  AddFrame(fStatusBar, new TGLayoutHints(kLHintsExpandX, 0, 0, 10, 0));

  MapSubwindows();
  Resize(GetDefaultSize());
  MapWindow();

  fEcanvas->Connect("TCanvas", "Closed()", "TApplication", gApplication, "Terminate()");

  dh2 = data->GetH2(); // default data histogram

  if (data->GetArgs()->IsSlice())
    slice = std::make_unique<DynamicSlice>(data->GetArgs()->GetSlice());
}

void MainFrame::GrabMouseWheel() const
{
  // Handle only buttons 4 and 5 used by the wheel mouse to scroll
  // see TileFrame::TileFrame in guitest.cxx
  gVirtualX->GrabButton(fId, kButton4, kAnyModifier,
			kButtonPressMask | kButtonReleaseMask,
			kNone, kNone);
  gVirtualX->GrabButton(fId, kButton5, kAnyModifier,
			kButtonPressMask | kButtonReleaseMask,
			kNone, kNone);
}

void MainFrame::SetGeometry(const std::shared_ptr<Geometry3> g)
{
  geo3 = g;
  if (geo3)
    gh2 = geo3->GetH2();
}

void MainFrame::SetGeometry(const std::shared_ptr<GeometryMultiGraph> g)
{
  plotgeom = g;
}


MainFrame::~MainFrame()
{
  // .help TGMainFrame::Cleanup
  // Cleanup and delete all objects contained in this composite frame.
  // This will delete all objects added via AddFrame().
  Cleanup();
}

TVirtualPad *MainFrame::GetHistogramPad() const
/*!
  Return the canvas pad with the 2D histgoram
 */
{
  TVirtualPad *c1 = GetCanvas();
  if (data->GetArgs()->IsSlice())
    return c1->GetPad(1);
  else
    return c1;
}

TVirtualPad *MainFrame::GetSlicePad() const
/*!
  Return the canvas pad with the slice (if any)
 */
{
  TVirtualPad *c1 = GetCanvas();
  if (data->GetArgs()->IsSlice())
    return c1->GetPad(2);
  else
    return nullptr;
}

void MainFrame::DoSlider()
{
  //  std::cout << __PRETTY_FUNCTION__ << ": DoSlider" << std::endl;
  const float y = fSlider->GetPosition();

  TVirtualPad *pad1 = GetHistogramPad();
  pad1->cd();

  dh2 = data->Draw(y);

  if (geo3)
    gh2 = geo3->Draw(y);
  else if (plotgeom)
    plotgeom->Draw();

  pad1->Update();
}

Bool_t MainFrame::ProcessMessage(Long_t msg, Long_t parm1, Long_t parm2)
{
  // Window_t wdummy;
  //  int ax, ay;
   // TRootHelpDialog *hd;
   // TGListTreeItem *item;
   // TGFileInfo fi;
   // Char_t  strtmp[250];

  if (!false) {
    std::cout << "Process: " << msg << " " << parm1 << " " << parm2 << std::endl;
    std::cout << "\tMSG: " << GET_MSG(msg) << " SUBMSG: " << GET_SUBMSG(msg) << std::endl;
    std::cout << "\t COMMAND: " << kC_COMMAND << " MENU: " << kCM_MENU << std::endl;
  }

  switch (GET_MSG(msg)) {
  case kC_HSLIDER: // 6, mouse wheel scroll, see gui/gui/inc/WidgetMessageTypes.h
    switch (GET_SUBMSG(msg)) {
    case kSL_POS:
      std::cout << __FUNCTION__ << ": kC_HSLIDER (kSL_POS)" << std::endl;
      DoSlider();
      break;
    }
    break;
  case kC_VSLIDER: // 7
    switch (GET_SUBMSG(msg)) {
    case kSL_RELEASE:
      std::cout << __FUNCTION__ << ": Mouse released" << std::endl;
      DoSlider();
      break;
    }
    break;
  case kC_COMMAND:
    switch (GET_SUBMSG(msg)) {
    case M_FILE_EXIT:
      std::cout << "file -> exit" << std::endl;
      gApplication->Terminate();
      break;
    case M_HELP_ABOUT:
      // std::cout << "Help" << std::endl;
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

  Int_t binx(0), biny(0);
  const Double_t x  = gPad->PadtoX(gPad->AbsPixeltoX(px));
  const Double_t y  = gPad->PadtoY(gPad->AbsPixeltoY(py));

  fStatusBar->SetText(Form("%s: %s", dh2->GetName(), dh2->GetTitle()),0);

  if (gh2)
    {
      binx = gh2->GetXaxis()->FindFixBin(x);
      biny = gh2->GetYaxis()->FindFixBin(y);
      fStatusBar->SetText(Form("Material: %d", static_cast<int>(gh2->GetBinContent(binx, biny))),1);
    }
  else if (plotgeom)
    fStatusBar->SetText("Geometry: PLOTGEOM",1);
  else
    fStatusBar->SetText("Geometry file not specified",1);


   char text2[50];
   if (event == kKeyPress)
     sprintf(text2, "%c %c", (char) px, (char) py);
   else
     sprintf(text2, "%d,%d", px, py);

   fStatusBar->SetText(text2,2);

   // data value and error

   binx = dh2->GetXaxis()->FindFixBin(x);
   biny = dh2->GetYaxis()->FindFixBin(y);

   const Double_t val = dh2->GetBinContent(binx, biny);
   const Double_t err = dh2->GetBinError(binx, biny);
   Double_t relerr = 100.0;
   if (std::abs(val)>0.0)
     relerr = err/val * 100.0;

   std::cout << spaces << '\r';
   if (data->GetArgs()->IsErrors()) {
     fStatusBar->SetText(Form("%g %%", val),3);
     std::cout << val << " % \r" << std::flush;
   }
   else {
     fStatusBar->SetText(Form("%g +- %.0f %%", val,relerr),3);
     std::cout << val << " ± " << err << "   " << std::setprecision(3) << relerr << " % \r" << std::flush;
   }

   if (slice)
     slice->Draw(dh2, GetHistogramPad(), GetSlicePad());
}

Bool_t MainFrame::HandleButton(Event_t *event)
{
  // Handle wheel mouse to scroll.

  if (!fSlider) return kTRUE; // no slider created (e.g. with the -max option or single bin)

  //std::cout << __PRETTY_FUNCTION__ << ": here" << std::endl;

  if (event->fCode == kButton4 || event->fCode == kButton5) { // 4=up, 5=down
    const float   y =  fSlider->GetPosition();
    const TAxis  *a = data->GetNormalAxis();
    const Int_t bin = a->FindBin(y);
    Double_t offset;
    Int_t direction;

    if (event->fCode == kButton4) { // scroll up
      //      std::cout << __PRETTY_FUNCTION__ << ": Button4 (scroll up)" << std::endl;
      direction = 1;
    } else { //if (event->fCode == kButton5) { // scroll down
      //      std::cout << __PRETTY_FUNCTION__ << ": Button5 (scroll down)" << std::endl;
      direction = -1;
    }
    offset = a->GetBinWidth(bin+direction);
    fSlider->SetPosition(y+direction*offset/2);
    DoSlider();
  }
  return kTRUE;
}
