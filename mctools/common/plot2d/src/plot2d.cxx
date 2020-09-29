#include <iostream>
#include <TROOT.h>
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

  TApplication theApp("App",&argc,const_cast<char**>(argv));

  MainFrame *mf = new MainFrame(gClient->GetRoot(), 800, 600);

  theApp.Run();

  //  delete mf;

  return 0;
}
