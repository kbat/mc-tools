#include <iostream>
#include <TROOT.h>
#include <TStyle.h>
#include <TApplication.h>
//#include <TRint.h>
#include "Arguments.h"
#include "MainFrame.h"

int main(int argc, const char **argv)
{

  Arguments args(argc, argv);

  if (args.IsHelp())
    return 0;

  if (!args.test())
    return 1;

  const po::variables_map vm = args.GetMap();

  //  gROOT->SetBatch(true);
  gStyle->SetOptStat(kFALSE);

  const size_t width = vm["width"].as<size_t>();
  size_t height = vm["height"].as<size_t>();
  if (height==0)
    height = int(width*2.0/(1.0+sqrt(5.0))); // golden ratio

  TApplication theApp("App",&argc,const_cast<char**>(argv));

  MainFrame *mf = new MainFrame(gClient->GetRoot(), 800, 600);
  mf->SetWindowName(args.GetTitle().c_str());

  theApp.Run();

  //  delete mf;

  return 0;
}
