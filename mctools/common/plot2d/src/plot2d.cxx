#include <iostream>

#include <boost/program_options.hpp>
#include <boost/algorithm/string/replace.hpp>

namespace po=boost::program_options;

struct Plane {
  Plane(std::string const &val):
    value(val)
  {
  }
  std::string value;
};

void validate(boost::any &v,
	      std::vector<std::string> const& values,
	      Plane*, int)
{
  using namespace boost::program_options;

  // Make sure no previous assignment to 'v' was made.
  validators::check_first_occurrence(v);

  // Extract the first string from 'values'. If there is more than
  // one string, it's an error, and exception will be thrown.
  std::string const& s = validators::get_single_string(values);

  const std::vector<std::string> planes{"xy", "xz" "yx", "yz", "zx", "zy"};

  if (std::find(planes.begin(), planes.end(), s)!=planes.end()) {
    v = boost::any(Plane(s));
  } else {
    throw validation_error(validation_error::invalid_option_value);
  }
}

po::variables_map options(int argc, const char **argv)
{
  Plane xy("xy");
  po::variables_map vm;
  try{
    //  options(argc, argv);
    po::options_description generic("Generic options");
    generic.add_options()
      ("help,h", "Show this help message and exit")
      ("plane", po::value<Plane>()->default_value(xy,"xy"), "Plane")
      ("title", po::value<std::string>()->default_value(""),"Plot title");

    po::options_description data("Data options");
    data.add_options()
      ("dfile", "Data file name")
      ("dhist", "Data histogram name")
      ("doption", po::value<std::string>()->default_value("colz"), "Data draw option")
      ("dcont", po::value<size_t>()->default_value(200), "Number of contour levels for data");

    po::options_description geom("Geometry options");
    geom.add_options()
      ("gfile", "Geometry file name")
      ("ghist", po::value<std::string>()->default_value("h3"), "Geometry histogram name")
      ("goption", po::value<std::string>()->default_value("cont3"), "Geometry draw option")
      ("gcont", po::value<size_t>()->default_value(25), "Number of contour levels for geometry")
      ("glwidth", po::value<size_t>()->default_value(2), "Geometry line width")
      ("glcolor", po::value<std::string>()->default_value("kBlack"), "Geometry line color");

    po::positional_options_description p;
    p.add("dfile", 1);
    p.add("dhist", 1);
    p.add("gfile", 1);
    p.add("ghist", 1);

    po::options_description all_options("Allowed options");
    all_options.add(generic).add(data).add(geom);

      //    po::store(po::parse_command_line(argc, argv, desc), vm);
    po::store(po::command_line_parser(argc, argv).
          options(all_options)
	      .positional(p)
	      .style(po::command_line_style::default_style | po::command_line_style::allow_long_disguise)
	      .run(), vm);
    po::notify(vm);

    if (vm.count ("help"))
      {
	std::stringstream stream;
	stream << all_options;
	std::string helpMsg = stream.str();
	boost::algorithm::replace_all(helpMsg, "--", "-");
	std::cout << helpMsg << std::endl;
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

  const std::string dfile = vm["dfile"].as<std::string>();
  const std::string dhist = vm["dhist"].as<std::string>();
  const std::string gfile = vm["gfile"].as<std::string>();
  const std::string ghist = vm["ghist"].as<std::string>();
  const std::string plane = vm["plane"].as<std::string>();

  std::cout << "dfile: " << dfile << std::endl;
  std::cout << "dhist: " << dhist << std::endl;
  std::cout << "gfile: " << gfile << std::endl;
  std::cout << "ghist: " << ghist << std::endl;
  std::cout << "plane: " << plane << std::endl;

  return 0;
}
