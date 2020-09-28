#include <iostream>
#include <TApplication.h>
#include "Arguments.h"
#include "MainFrame.h"

int main(int argc, const char **argv)
{

  Arguments args(argc, argv);
  const po::variables_map vm = args.GetMap();

  if (vm.count("help"))
    return 0;

  args.test();


  TApplication theApp("App",&argc,const_cast<char**>(argv));

  MainFrame *mf = new MainFrame(gClient->GetRoot(), 800, 600);

  theApp.Run();

  delete mf;

  return 0;
}
