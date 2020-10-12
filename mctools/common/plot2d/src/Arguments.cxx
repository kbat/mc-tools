#include <cmath>
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
  const size_t inan = std::numeric_limits<size_t>::quiet_NaN();

  const float flowest = std::numeric_limits<float>::lowest();
  const float fmax = std::numeric_limits<float>::max();

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
      ("title", po::value<std::string>()->default_value("None"), "Plot title")
      ("xtitle", po::value<std::string>()->default_value("None"), "Horizontal axis title")
      ("ytitle", po::value<std::string>()->default_value("None"), "Vertical axis title")
      ("ztitle", po::value<std::string>()->default_value("None"), "Colour axis title")
      ("xmin", po::value<float>()->default_value(flowest), "Horizontal axis min value")
      ("xmax", po::value<float>()->default_value(fmax), "Horizontal axis max value")
      ("ymin", po::value<float>()->default_value(flowest), "Vertical axis min value")
      ("ymax", po::value<float>()->default_value(fmax), "Vertical axis max value")
      ("zmin", po::value<float>()->default_value(flowest), "Colour axis min value")
      ("zmax", po::value<float>()->default_value(fmax), "Colour axis max value")
      ("width", po::value<size_t>()->default_value(800), "Canvas width")
      ("height", po::value<size_t>()->default_value(inan), "Canvas height. If not specified, it is calculated from the width with the golden ratio rule.")
      ("right_margin", po::value<float>()->default_value(0.12f), "Right margin of the canvas in order to allocate enough space for the z-axis title. Used only if ZTITLE is set and DOPTION is \"colz\"")
      ("flip", "Flip the vertical axis")
      ("bgcolor", "Set the frame background colour to some hard-coded value")
      ("o", po::value<std::string>()->default_value("None"), "Output file name. If given then the canvas is not shown.")
      ("v", "Explain what is being done")
      ("slice", po::value<std::vector<short> >()->multitoken()->default_value(std::vector<short>({0}), "no slice"), "Show live slice averaging the given number of bins. Left mouse click on the 2D histogram swaps axes, middle button click swaps logy. Two integer numbers are required: the first one is the number of bins to average the slice on 2D histogrm, the second one indicates how many bins of this have to be merged into one bin in the 1D histogram")
      ("errors", "Plot the histogram with relative errors instead of data");


    po::options_description data("Data options", w.ws_col);
    data.add_options()
      ("scale", po::value<float>()->default_value(1.0), "Data scaling factor")
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
    try {
      po::notify(vm);
    } catch (boost::program_options::error& e) {
      std::cout << "Error: " << e.what() << "\n";
      exit(1);
    }

    if (help || vm.count ("help"))
      {
	help = true;
	std::stringstream stream;
	stream << all_options;
	std::string helpMsg = stream.str();
	boost::algorithm::replace_all(helpMsg, "--", "-");
	boost::algorithm::replace_all(helpMsg, "-dfile", " dfile");
	boost::algorithm::replace_all(helpMsg, "-dhist", " dhist");
	boost::algorithm::replace_all(helpMsg, "-gfile", " gfile");
	boost::algorithm::replace_all(helpMsg, "-ghist", " ghist");
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
  const float xmin = vm["xmin"].as<float>();
  const float xmax = vm["xmax"].as<float>();
  const float ymin = vm["ymin"].as<float>();
  const float ymax = vm["ymax"].as<float>();

  bool val = CheckMinMax(xmin, xmax, "x") && CheckMinMax(ymin, ymax, "y");

  val = val & CheckSlice();

  //  const std::string dfile = vm["dfile"].as<std::string>();
  // const std::string dhist = vm["dhist"].as<std::string>();
  // const std::string gfile = vm["gfile"].as<std::string>();
  // const std::string ghist = vm["ghist"].as<std::string>();
  // const Plane plane = vm["plane"].as<Plane>();
  // const std::string title = vm["title"].as<std::string>();

  // std::cout << "dfile: " << dfile << std::endl;
  // std::cout << "dhist: " << dhist << std::endl;
  // std::cout << "gfile: " << gfile << std::endl;
  // std::cout << "ghist: " << ghist << std::endl;
  // std::cout << "plane: " << plane << std::endl;
  // std::cout << "title: " << title << std::endl;

  return val;
}

bool Arguments::CheckMinMax(const float &vmin, const float &vmax, const std::string &title) const
{
  constexpr float flowest = std::numeric_limits<float>::lowest();
  constexpr float fmax = std::numeric_limits<float>::max();
  constexpr float epsilon = std::numeric_limits<float>::epsilon();
  bool val = true;

  if ((std::abs(vmin-flowest)>epsilon) && (std::abs(vmax-fmax)<epsilon)) {
    std::cerr << "Error: both " << title << "min and " << title << "max must be set" << std::endl;
    val = false;
  } else if ((std::abs(vmin-flowest)<epsilon) && (std::abs(vmax-fmax)>epsilon)) {
    std::cerr << "Error: both " << title << "min and " << title << "max must be set" << std::endl;
    val = false;
  } else if (vmin>=vmax) {
    std::cerr << "Error: " << title << "min must be < " << title << "max" << std::endl;
    val = false;
  }

  if (!val) {
    std::cerr << "\t" << title << "min: " << vmin << std::endl;
    std::cerr << "\t" << title << "max: " << vmax << std::endl;
  }

  return val;
}

bool Arguments::CheckSlice() const
{
  const std::vector<short> slice = GetSlice();
  size_t size = slice.size();

  if ((size == 1) && (slice[0] == 0)) // default value - slice not specified
    return true;
  else if (size != 2) {
    std::cerr << "Error: -slice argument needs 2 integers" << std::endl;
    return false;
  } else if ((slice[0]<1) || (slice[1]<1)) {
    std::cerr << "Error: -slice values must be positive" << std::endl;
    return false;
  }

  return true;
}

std::string Arguments::GetWindowTitle() const
{
  const std::string title = "plot2d: " + vm["dfile"].as<std::string>() + " " +
    vm["dhist"].as<std::string>() + " " +
    vm["plane"].as<Plane>().GetValue();

  return title;
}

size_t Arguments::GetHeight() const
{
  size_t width = GetWidth();
  size_t height = vm["height"].as<size_t>();

  if (height==0) {
    constexpr float sqrt5 = 2.236068;
    height = round(width*2.0/(1.0+sqrt5)); // golden ratio
  }

  return height;
}

bool Arguments::IsSlice() const
{
  /*
    Return true if slice is needed
   */
  const std::vector<short> slice = GetSlice();

  return (!((slice.size() == 1) && (slice[0] == 0)));
}
