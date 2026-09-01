#include <TApplication.h>
#include <TGClient.h>
#include <TCanvas.h>
#include <TF1.h>
#include <TRandom.h>
#include <TGButton.h>
#include <TRootEmbeddedCanvas.h>
#include <TAxis.h>

#include "MainFrame.h"
#include "Chrono.h"

#include <algorithm>

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
  TGMainFrame(p,w,h), fSlider(nullptr), data(data), geo(nullptr), slice(nullptr),
  lastpixel(-1,-1), lastbin(-1,-1)
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

      fSlider = new TGVSlider(hframe, 40, kSlider1 | kScaleBoth);
      fSlider->Associate(this);
      // in bin numbers counted from the top - see CoordToSlider()
      fSlider->SetRange(1, nbins);
      fSlider->SetPosition(CoordToSlider(data->GetOffset()));
      /*
	The tick marks are spaced in pixels, not in bins: one per bin, but
	never closer together than this - a fine mesh would otherwise draw a
	tick on every pixel row and leave the scale a solid bar.
      */
      const Int_t minspacing = 25;
      fSlider->SetScale(std::max<Int_t>(minspacing, h/nbins));
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
  data->Prefetch(data->GetOffset()); // the first move of the slider is then free
  ShowH2Name();

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

  // without a geometry this part of the status bar never says anything else
  if (!geo)
    fStatusBar->SetText("Geometry file not specified", 1);
}

void MainFrame::ShowH2Name()
/*!
  Put the name and the title of the histogram now on the canvas into the status
  bar.

  It only changes when another slice is drawn, so it is written from there
  rather than from EventInfo(), which runs on every motion event.  What the
  pointer was last seen over goes with it: the value EventInfo() showed was
  read from the slice that has just been replaced.
 */
{
  fStatusBar->SetText(Form("%s: %s", dh2->GetName(), dh2->GetTitle()), 0);

  lastpixel = {-1, -1};
  lastbin = {-1, -1};
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

Bool_t MainFrame::OnHistogramPad(Int_t px, Int_t py) const
/*!
  Is the given canvas pixel inside the pad holding the data histogram?

  gPad cannot answer this.  It is the pad ROOT last selected, and on a plain
  motion event that is still the pad the pointer has already left: only the
  enter and leave events carry the pad it is really over.  Reading gPad instead
  is how the status bar came to show a value and a region for a point of the
  -slice projection, converted as though it were a point of the plot.

  The pad knows whereabouts on the canvas it is, so ask it instead.
 */
{
  const TVirtualPad *pad = GetHistogramPad();

  // v runs up the pad and pixels run down the canvas, so v=1 is the top edge
  return (px >= pad->UtoAbsPixel(0.0)) && (px <= pad->UtoAbsPixel(1.0)) &&
         (py >= pad->VtoAbsPixel(1.0)) && (py <= pad->VtoAbsPixel(0.0));
}

Int_t MainFrame::CoordToSlider(Double_t x) const
{
  const TAxis *a = data->GetNormalAxis();
  const Int_t nbins = a->GetNbins();

  // an offset on the edge of the axis falls into the underflow/overflow bin
  const Int_t bin = std::min(nbins, std::max(1, a->FindBin(x)));

  return nbins + 1 - bin;
}

Double_t MainFrame::SliderToCoord(Int_t pos) const
{
  const TAxis *a = data->GetNormalAxis();
  const Int_t nbins = a->GetNbins();

  return a->GetBinCenter(nbins + 1 - std::min(nbins, std::max(1, pos)));
}

void MainFrame::DoSlider()
{
  //  std::cout << __PRETTY_FUNCTION__ << ": DoSlider" << std::endl;
  const Double_t y = SliderToCoord(fSlider->GetPosition());

  data->SetOffset(y);

  TVirtualPad *pad1 = GetHistogramPad();
  pad1->cd();

  dh2 = data->Draw(y);
  ShowH2Name();

  if (geo)
    geo->Draw(y);

  /*
    Painting the picture is what a slice change actually costs - ROOT draws one
    box per bin, so it is linear in the size of the projection and, on a mesh
    of a few hundred bins each way, an order of magnitude more than projecting
    the data and cutting the geometry put together.  -rebin is the only lever
    on it, so -v says how big it is.
  */
  {
    Chrono t(data->GetArgs()->IsVerbose(), " MainFrame: repaint");
    pad1->Update();
  }

  /*
    The slider is most likely to move on to one of the neighbouring slices, so
    project them while the user is looking at this one.  After Update(), so
    that the picture is on the screen before the worker threads take the cores.
  */
  data->Prefetch(y);
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
    /*!
      Only the release of the slider redraws: a live drag would cut the
      geometry once per bin it went past, and one cut takes a noticeable
      fraction of a second.  The mouse wheel does not come through here at all
      - see HandleButton().
    */
  case kC_VSLIDER: // 7, see gui/gui/inc/WidgetMessageTypes.h
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
    break;
  default:
    break;
  }
  return kTRUE;
}

void MainFrame::EventInfo(EEventType event, Int_t px, Int_t py, TObject *selected)
/*!
  Writes the event status in the status bar parts.

  This runs on every motion event, so nothing is written that cannot have
  changed since the last one.  The name of the histogram is not written here at
  all - ShowH2Name() does that when another slice is drawn.  The region under
  the pointer is sampled far more finely than the data mesh, so it goes with
  the pixel; the value under the pointer only with the bin, which also keeps
  the line printed to the terminal - a flushed write per event, the most
  expensive thing in here - down to the times it has something new to say.
 */
{
  (void)selected;

  const bool moved = (px != lastpixel.first) || (py != lastpixel.second);
  lastpixel = {px, py};

   if (event == kKeyPress)
     fStatusBar->SetText(Form("%c %c", static_cast<char>(px), static_cast<char>(py)), 2);
   else if (moved)
     fStatusBar->SetText(Form("%d,%d", px, py), 2);

   /*!
     The region and the value are read at a point of the data histogram, so
     they may only be read while the pointer is over its pad - with -slice the
     canvas is divided, and below the plot lies the projection, whose
     coordinates name something else entirely.  What was last read over the
     plot stays in the status bar meanwhile.
   */
   TVirtualPad *h2pad = GetHistogramPad();
   const bool onh2 = OnHistogramPad(px, py);

   if (onh2)
     {
       const Double_t x  = h2pad->PadtoX(h2pad->AbsPixeltoX(px));
       const Double_t y  = h2pad->PadtoY(h2pad->AbsPixeltoY(py));

       if (moved && geo)
	 fStatusBar->SetText(geo->StatusText(x, y).data(), 1);

       // data value and error

       const Int_t binx = dh2->GetXaxis()->FindFixBin(x);
       const Int_t biny = dh2->GetYaxis()->FindFixBin(y);

       if ((binx != lastbin.first) || (biny != lastbin.second))
	 {
	   lastbin = {binx, biny};

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
	     /*
	       setprecision() stays on the stream, so setting it here used to
	       round down every later line hplot printed - the -v min and max
	       among them.  Format the one number that wants it instead.
	     */
	     std::cout << val << " ± " << err << "   "
		       << Form("%.3g", relerr) << " % \r" << std::flush;
	   }
	 }
     }

   /*!
     The middle mouse button pops the object under the cursor - usually the
     data histogram - to the end of the list of primitives of its pad
     (TCanvas::HandleInput), so that it is painted last, hiding the geometry
     drawn on top of it.  Put the geometry back in front.
   */
   if (geo && ((event == kButton2Down) || (event == kButton2Up)) && onh2) {
     geo->Pop();
     h2pad->Modified();
     h2pad->Update();
     h2pad->cd(); // Update() may leave another pad current
   }

   /*
     The live slice follows the pointer over the plot, and only there - the
     same reason the readings above do.  Off the plot the lines marking the
     band it projects have to go: nothing else takes them off the screen, and
     they would otherwise sit there pointing at a band the pointer has left.

     kMouseLeave is asked about as well as the pad, because the pointer can
     leave the canvas through the top or a side edge of the plot - the leave
     event then carries a pixel OnHistogramPad() still calls its own.
   */
   if (slice) {
     if (onh2 && (event != kMouseLeave))
       slice->Draw(dh2, h2pad, GetSlicePad());
     else
       slice->Erase(h2pad);
   }
}

Bool_t MainFrame::HandleButton(Event_t *event)
/*!
  Move the slider by one bin per notch of the mouse wheel.

  GrabMouseWheel() asks for both the press and the release of buttons 4 and 5,
  and every notch delivers both, so only one of the two may be acted upon -
  otherwise a notch would step two bins.

  Anything else goes to the base class rather than being swallowed here.
 */
{
  // no slider created (e.g. with the -max option or a single bin)
  if (!fSlider || (event->fType != kButtonPress))
    return TGMainFrame::HandleButton(event);

  Int_t step;
  if (event->fCode == kButton4)       // wheel up: the knob goes up, and the
    step = -1;                        // slider counts downwards
  else if (event->fCode == kButton5)  // wheel down
    step = +1;
  else
    return TGMainFrame::HandleButton(event);

  const Int_t pos = fSlider->GetPosition() + step;
  if ((pos < fSlider->GetMinPosition()) || (pos > fSlider->GetMaxPosition()))
    return kTRUE; // already at the end of the axis - nothing to redraw

  fSlider->SetPosition(pos);
  DoSlider();

  return kTRUE;
}
