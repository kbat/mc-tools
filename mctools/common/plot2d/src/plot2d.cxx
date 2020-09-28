#include <iostream>
#include "Arguments.h"

int main(int argc, const char **argv)
{

  Arguments args(argc, argv);
  const po::variables_map vm = args.GetMap();

  if (vm.count("help"))
    return 0;

  args.test();

  return 0;
}
