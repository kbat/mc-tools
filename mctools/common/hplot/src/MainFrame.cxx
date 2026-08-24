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

/*!
  Blanks used to wipe the line before reprinting the value under the cursor.
  A char would overflow on terminals wider than 128 columns, making the
  std::string construction below undefined.
*/
const int line_width = getenv("COLUMNS") ? std::max(1, atoi(getenv("COLUMNS"))-1) : 80-1;
const std::string spaces(line_width, ' ');

MainFrame::MainFrame(const TGWindow *p, UInt_t w, UInt_t h,
		     const std::shared_ptr<Data3> data) :
  TGMainFrame(p,w,h), fSlider(nullptr), data(data), geo(nullptr), slice(nullptr)
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

  // there is nothing to slide through with the -max option, which collapses
  // the normal axis, or when that axis has a single bin
  const TAxis *a  = data->GetNormalAxis();
  if (!data->GetArgs()->IsMax() && (a->GetNbins()>1))
    {
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

  dh2 = data->GetH2(); // default data histogram

  if (data->GetArgs()->IsSlice())
    slice = std::make_unique<DynamicSlice>(data->GetArgs()->GetSlice(0),
					   data->GetArgs()->GetSlice(1));
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

void MainFrame::SetGeometry(const std::shared_ptr<Geometry> g)
{
  geo = g;
}


void MainFrame::CloseWindow()
/*!
  Called when the window manager closes the window.

  The default implementation deletes the frame, which would leave the event
  loop running without a window - and delete an object owned by Application.
  Leaving the event loop instead unwinds the normal way, through Run().
 */
{
  gApplication->Terminate(0);
}

MainFrame::~MainFrame()
{
  TCanvas *c1 = GetCanvas();

  /*
    The embedded canvas does not own the TCanvas handed to it, so the canvas
    would outlive this window and be deleted by TROOT::EndOfProcessCleanups()
    at exit - after the interpreter globals have been reset, and with its
    container window already gone.  Take it down here, while it is still
    consistent, and drop the connection to this frame first: EventInfo() must
    not be called on a half-destructed MainFrame.
  */
  c1->Disconnect("ProcessedEvent(Int_t,Int_t,Int_t,TObject*)", this,
		 "EventInfo(EEventType,Int_t,Int_t,TObject*)");
  delete c1;

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

  if (geo)
    geo->Draw(y);

  pad1->Update();
}

Bool_t MainFrame::ProcessMessage(Long_t msg, Long_t parm1, Long_t parm2)
{
  const bool verbose = data->GetArgs()->IsVerbose();

  if (verbose) {
    std::cout << "Process: " << msg << " " << parm1 << " " << parm2 << std::endl;
    std::cout << "\tMSG: " << GET_MSG(msg) << " SUBMSG: " << GET_SUBMSG(msg) << std::endl;
    std::cout << "\t COMMAND: " << kC_COMMAND << " MENU: " << kCM_MENU << std::endl;
  }

  switch (GET_MSG(msg)) {
  case kC_HSLIDER: // 6, mouse wheel scroll, see gui/gui/inc/WidgetMessageTypes.h
    switch (GET_SUBMSG(msg)) {
    case kSL_POS:
      DoSlider();
      break;
    }
    break;
  case kC_VSLIDER: // 7
    switch (GET_SUBMSG(msg)) {
    case kSL_RELEASE:
      DoSlider();
      break;
    }
    break;
  case kC_COMMAND:
    switch (GET_SUBMSG(msg)) {
    case M_FILE_EXIT:
      gApplication->Terminate();
      break;
    case M_HELP_ABOUT:
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

  (void)selected;

  const Double_t x  = gPad->PadtoX(gPad->AbsPixeltoX(px));
  const Double_t y  = gPad->PadtoY(gPad->AbsPixeltoY(py));

  fStatusBar->SetText(Form("%s: %s", dh2->GetName(), dh2->GetTitle()),0);

  if (geo)
    fStatusBar->SetText(geo->StatusText(x, y).data(), 1);
  else
    fStatusBar->SetText("Geometry file not specified", 1);

   if (event == kKeyPress)
     fStatusBar->SetText(Form("%c %c", static_cast<char>(px), static_cast<char>(py)), 2);
   else
     fStatusBar->SetText(Form("%d,%d", px, py), 2);

   // data value and error

   const Int_t binx = dh2->GetXaxis()->FindFixBin(x);
   const Int_t biny = dh2->GetYaxis()->FindFixBin(y);

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
