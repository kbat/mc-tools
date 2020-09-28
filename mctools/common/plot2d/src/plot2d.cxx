#include <iostream>
// #include <vector>
// #include <cmath>
// #include <algorithm>
// #include <numeric>
// #include <chrono>
// #include <limits>

#include <boost/program_options.hpp>
namespace po=boost::program_options;

po::variables_map options(int argc, const char **argv)
{
  po::variables_map vm;
  std::string plane;
  try{
    //  options(argc, argv);
    po::options_description desc("Allowed options");
    desc.add_options()
      ("dfile", "Data file name")
      ("help,h", "produce help message")
      ("plane", po::value<std::string>(&plane)->default_value("xy"),"Plane");

    po::positional_options_description p;
    p.add("dfile", -1);

      //    po::store(po::parse_command_line(argc, argv, desc), vm);
    po::store(po::command_line_parser(argc, argv).
          options(desc).positional(p).run(), vm);
    po::notify(vm);

    if (vm.count("help")) {
      std::cout << desc << "\n";
      return vm;
    }
  }
  catch(std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    //    return 1;
  }
  catch(...) {
    std::cerr << "Exception of unknown type!\n";
    //    return 2;
  }

  return vm;
}


int main(int argc, const char **argv)
{

  po::variables_map vm = options(argc, argv);
  if (vm.count("help"))
    return 0;

  const std::string plane = vm["plane"].as<std::string>();

  std::cout << plane << std::endl;

  std::cout << "hi" << std::endl;
  return 0;
}
