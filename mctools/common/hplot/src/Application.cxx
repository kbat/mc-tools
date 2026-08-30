#include <TError.h>
#include <TGClient.h>
#include <TH1.h>
#include <TStyle.h>

#include "Application.h"
#include "Chrono.h"
#include "GeometryCSG.h"
#include "Palette.h"

Application::Application(const std::shared_ptr<Arguments>& args) :
  args(args), canvas(nullptr), theApp(nullptr), mf(nullptr)
{
  gStyle->SetOptStat(kFALSE);
  SetColourMap(args->GetPalette());

  /*
    Every histogram here is owned by a shared_ptr, so none of them may also be
    registered in the current directory and deleted a second time when it goes
    - which is what happens if one is created while a TFile is open.  This says
    so once, before the first of them exists.
  */
  TH1::AddDirectory(kFALSE);

  data = std::make_shared<Data3>(args->GetDataFile(), args->GetDataHist(), args);

  /*
    Reading the geometry and cutting it does not touch ROOT, so the cut runs on
    a worker thread while the data are projected here - by the time the first
    picture is drawn it is usually waiting rather than the other way round.
  */
  if (!args->GetGeoFile().empty())
    {
      Chrono t(args->IsVerbose(), "GeometryCSG");
      auto g = std::make_shared<GeometryCSG>(args, data);
      g->Prefetch(data->GetOffset());
      geo = g;
    }

  {
    Chrono t(args->IsVerbose(), "Data3::Project");
    data->Project();
  }
}

TVirtualPad *Application::SetUpCanvas(int& argc, const char **argv)
/*!
  Create the canvas - on its own in batch mode, inside the main window
  otherwise - and return the pad the 2D histogram goes into.
 */
{
  const UInt_t width  = args->GetWidth();
  const UInt_t height = args->GetHeight();

  if (args->IsBatch())
    {
      canvas = new TCanvas("hplot", args->GetWindowTitle().data(), width, height);
    }
  else
    {
      theApp = new TApplication("hplot", &argc, const_cast<char**>(argv), nullptr, -1);

      mf = std::make_unique<MainFrame>(gClient->GetRoot(), width, height, data);
      mf->SetGeometry(geo);
      mf->SetWindowName(args->GetWindowTitle().data());

      canvas = mf->GetCanvas();
    }

  TVirtualPad *h2pad = canvas;

  if (args->IsSlice() && !args->IsBatch())
    {
      canvas->Divide(1,2);
      canvas->cd(1);
      h2pad = canvas->GetPad(1);
    }

  if (args->IsZTitle())
    canvas->SetRightMargin(args->GetRightMargin());

  return h2pad;
}

void Application::Print()
{
  const Int_t oldLevel = gErrorIgnoreLevel;
  gErrorIgnoreLevel = kWarning; // suppress the "Info in <TCanvas::Print>" message
  canvas->Print(args->GetOutputFile().data());
  gErrorIgnoreLevel = oldLevel;

  delete canvas;
  canvas = nullptr;
}

int Application::Run(int& argc, const char **argv)
{
  TVirtualPad *h2pad = SetUpCanvas(argc, argv);

  data->Draw();

  h2pad->SetLogz(args->IsLogz() && !args->IsErrors());

  if (geo)
    geo->Draw();

  if (args->IsBatch())
    Print();
  else
    theApp->Run(kTRUE);

  return 0;
}
