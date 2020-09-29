#include "Arguments.h"

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

  const std::array<std::string,6> planes{"xy", "xz" "yx", "yz", "zx", "zy"};

  if (std::find(planes.begin(), planes.end(), s)!=planes.end()) {
    v = boost::any(Plane(s));
  } else {
    std::cerr << "plane: " << s << std::endl;
    throw validation_error(validation_error::invalid_option_value);
  }
}

Arguments::Arguments(int ac, const char **av) :
  argc(ac), argv(av), help(false)
{
  Plane xy("xy");
  const float fnan = std::numeric_limits<float>::quiet_NaN();
  const std::string snan = std::numeric_limits<std::string>::quiet_NaN();
  const size_t inan = std::numeric_limits<size_t>::quiet_NaN();

  //  po::variables_map vm;
  struct winsize w;
  ioctl(STDOUT_FILENO, TIOCGWINSZ, &w);

  try{
    //  options(argc, argv);
    po::options_description hidden("Positional arguments");
    hidden.add_options()
      ("dfile", "Data file name")
      ("dhist", "Data histogram name")
      ("gfile", "Geometry file name")
      ("ghist", po::value<std::string>()->default_value("h3"), "Geometry histogram name");

    po::options_description generic("Generic options", w.ws_col);
    generic.add_options()
      ("help,h", "Show this help message and exit")
      ("plane", po::value<Plane>()->default_value(xy, "xy"),  "Plane")
      ("title", po::value<std::string>()->default_value(snan), "Plot title")
      ("xtile", po::value<std::string>()->default_value(snan), "Horizontal axis title")
      ("ytile", po::value<std::string>()->default_value(snan), "Vertical axis title")
      ("ztile", po::value<std::string>()->default_value(snan), "Colour axis title")
      ("xmin", po::value<float>()->default_value(fnan), "Horizontal axis min value")
      ("xmax", po::value<float>()->default_value(fnan), "Horizontal axis max value")
      ("ymin", po::value<float>()->default_value(fnan), "Vertical axis min value")
      ("ymax", po::value<float>()->default_value(fnan), "Vertical axis max value")
      ("zmin", po::value<float>()->default_value(fnan), "Colour axis min value")
      ("zmax", po::value<float>()->default_value(fnan), "Colour axis max value")
      ("width", po::value<size_t>()->default_value(800), "Canvas width")
      ("height", po::value<size_t>()->default_value(inan), "Canvas height. If not specified, it is calculated from the width with the golden ratio rule.")
      ("right_margin", po::value<float>()->default_value(0.12), "Right margin of the canvas in order to allocate enough space for the z-axis title. Used only if ZTITLE is set and DOPTION is \"colz\"")
      ("flip", "Flip the vertical axis")
      ("bgcolor", "Set the frame background colour to some hard-coded value")
      ("o", po::value<std::string>()->default_value(snan), "Output file name. If given then the canvas is not shown.")
      ("v", "Explain what is being done")
      ("slice", po::value<std::vector<size_t> >()->multitoken(), "Show live slice averaging the given number of bins. Left mouse click on the 2D histogram swaps axes, middle button click swaps logy. Two integer numbers are required: the first one is the number of bins to average the slice on 2D histogrm, the second one indicates how many bins of this have to be merged into one bin in the 1D histogram")
      ("errors", "Plot the histogram with relative errors instead of data");


    po::options_description data("Data options", w.ws_col);
    data.add_options()
      ("doption", po::value<std::string>()->default_value("colz"), "Data draw option")
      ("dcont", po::value<size_t>()->default_value(200), "Number of contour levels for data")
      ("no-logz", po::value<bool>()->default_value(false), "Remove log scale for the data colour axis");

    po::options_description geom("Geometry options", w.ws_col);
    geom.add_options()
      ("goption", po::value<std::string>()->default_value("cont3"), "Geometry draw option")
      ("gcont", po::value<size_t>()->default_value(25), "Number of contour levels for geometry")
      ("glwidth", po::value<size_t>()->default_value(2), "Geometry line width")
      ("glcolor", po::value<std::string>()->default_value("kBlack"), "Geometry line color");

    std::array<std::string, 4> positional_args{"dfile", "dhist", "gfile", "ghist"};
    po::positional_options_description p;
    for (const std::string& pa : positional_args)
      p.add(pa.c_str(), 1);

    po::options_description all_options("Usage: plot2d [options] dfile dhist gfile [ghist]");
    all_options.add(generic).add(data).add(geom).add(hidden);

    //    po::store(po::parse_command_line(argc, argv, desc), vm);
    auto parsed = po::command_line_parser(argc, argv).options(all_options).positional(p)
      .style(po::command_line_style::allow_short |
	     po::command_line_style::short_allow_adjacent |
	     po::command_line_style::short_allow_next |
	     po::command_line_style::allow_long |
	     po::command_line_style::long_allow_adjacent |
	     po::command_line_style::long_allow_next |
	     po::command_line_style::allow_sticky |
	     po::command_line_style::allow_dash_for_short |
	     po::command_line_style::allow_long_disguise)
      .run();

    for (const std::string& pa : positional_args)
      {
	auto it = std::find_if(parsed.options.begin(), parsed.options.end(),
			       [&pa](po::option const& o) {
				 return o.string_key == pa;
			       });
	if ((it == parsed.options.end()) && (pa!="ghist")) // ghist is optional
	  {
	    std::cerr << "Error: Missing positional argument \"" <<
	      pa << "\"\n" << std::endl;
	    help=true;
	    break;
	  }
      }

    po::store(parsed, vm);
    po::notify(vm);

    if (help || vm.count ("help"))
      {
	help = true;
	std::stringstream stream;
	stream << all_options;
	std::string helpMsg = stream.str();
	boost::algorithm::replace_all(helpMsg, "--", "-");
	std::cout << helpMsg << std::endl;
	return;
      }
  }
  catch(std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return;
  }
  catch(...) {
    std::cerr << "Exception of unknown type!\n";
    return;
  }

  return;
}

bool Arguments::test() const
{
  std::clog << "Arguments::test()" << std::endl;

  const std::string dfile = vm["dfile"].as<std::string>();
  const std::string dhist = vm["dhist"].as<std::string>();
  const std::string gfile = vm["gfile"].as<std::string>();
  const std::string ghist = vm["ghist"].as<std::string>();
  const Plane plane = vm["plane"].as<Plane>();
  const std::string title = vm["title"].as<std::string>();

  std::cout << "dfile: " << dfile << std::endl;
  std::cout << "dhist: " << dhist << std::endl;
  std::cout << "gfile: " << gfile << std::endl;
  std::cout << "ghist: " << ghist << std::endl;
  std::cout << "plane: " << plane << std::endl;
  std::cout << "title: " << title << std::endl;

  return true;
}
