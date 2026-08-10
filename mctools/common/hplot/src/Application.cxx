#include <TError.h>
#include <TGClient.h>
#include <TStyle.h>

#include "Application.h"
#include "Chrono.h"
#include "GeometryFactory.h"
#include "Palette.h"

Application::Application(const std::shared_ptr<Arguments>& args) :
  args(args), canvas(nullptr), theApp(nullptr), mf(nullptr)
{
  gStyle->SetOptStat(kFALSE);
  SetColourMap(args->GetPalette());

  data = std::make_shared<Data3>(args->GetDataFile(), args->GetDataHist(), args);
  {
    Chrono t(args->IsVerbose(), "Data3::Project");
    data->Project();
  }

  geo = MakeGeometry(args, data);
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
