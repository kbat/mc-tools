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

  const std::array<std::string,6> planes{"xy", "xz", "yx", "yz", "zx", "zy"};

  if (std::find(planes.begin(), planes.end(), s)!=planes.end()) {
    v = boost::any(Plane(s));
  } else {
    std::cerr << "plane: " << s << std::endl;
    throw validation_error(validation_error::invalid_option_value);
 }
}

void conflicting_options(const boost::program_options::variables_map & vm,
                         const std::string & opt1, const std::string & opt2)
/*!
  Function used to check that 'opt1' and 'opt2' are not specified at the same time.
  https://www.boost.org/doc/libs/1_55_0/libs/program_options/example/real.cpp
 */
{
  if (vm.count(opt1) && !vm[opt1].defaulted() &&
      vm.count(opt2) && !vm[opt2].defaulted())
    {
      throw std::logic_error(std::string("Conflicting options '") +
      			     opt1 + "' and '" + opt2 + "'.");
    }
}

Arguments::Arguments(int ac, const char **av) :
  argc(ac), argv(av), help(false), errors(false)
{
  Plane xy("xy");
  const size_t inan = std::numeric_limits<size_t>::quiet_NaN();

  const float flowest = std::numeric_limits<float>::lowest();
  const float fmax = std::numeric_limits<float>::max();

  //  po::variables_map vm;
  struct winsize w;
  ioctl(STDOUT_FILENO, TIOCGWINSZ, &w);

  try {
    //  options(argc, argv);
    po::options_description hidden("Positional arguments");
    hidden.add_options()
      ("dfile", "Data file name")
      ("dhist", "Data histogram name")
      ("gfile", po::value<std::string>()->default_value(""), "Geometry file name")
      ("ghist", po::value<std::string>()->default_value("h3"), "Geometry histogram name");

    po::options_description generic("Generic options", w.ws_col);
    generic.add_options()
      ("help,h", "Show this help message and exit.")
      ("plane", po::value<Plane>()->default_value(xy, "xy"),
       "Projection plane. Allowed values: xy, xz, yx, yz, zx, zy. The ROOT notation is used, i.e. the first symbol corresponds to the verical axis and the second symbol - to the horizontal axis of TH2.")
      ("offset", po::value<std::string>()->default_value("0.0"),
       "Offset of projection plane from origin. "
       " Either a float number or min/max/centre strings can be used. "
       "centre = (max+min)/2, min corresponds to the centre of the first bin, "
       "and max - to the last bin of the axis perpendicular to the projection plane. "
       "With the '-max' option offset applies to the geometry histogram only which allows to select "
       "the representative geometry view.")
      ("title", po::value<std::string>()->default_value("None"), "Plot title.")
      ("xtitle", po::value<std::string>()->default_value("None"), "Horizontal axis title.")
      ("ytitle", po::value<std::string>()->default_value("None"), "Vertical axis title.")
      ("ztitle", po::value<std::string>()->default_value("None"), "Colour axis title.")
      ("xmin", po::value<float>()->default_value(flowest), "Horizontal axis min value.")
      ("xmax", po::value<float>()->default_value(fmax), "Horizontal axis max value.")
      ("ymin", po::value<float>()->default_value(flowest), "Vertical axis min value.")
      ("ymax", po::value<float>()->default_value(fmax), "Vertical axis max value.")
      ("zmin", po::value<float>()->default_value(flowest), "Colour axis min value.")
      ("zmax", po::value<float>()->default_value(fmax), "Colour axis max value.")
      ("width", po::value<size_t>()->default_value(800), "Canvas width.")
      ("height", po::value<size_t>()->default_value(inan),
       "Canvas height. If not specified, it is calculated from the width with the golden ratio rule.")
      ("rebin", "Rebin the 2D histograms such that they are not larger than width x height "
       "(specified by the above arguments). This argument drastically speeds up histogram drawing, "
       "especially in the case when the data or geometry histograms are larger "
       "than the screen resolution.")
      ("right_margin", po::value<float>()->default_value(0.12),
       "Right margin of the canvas in order to allocate enough space for the TH2 z-axis title. "
       "Used only if ZTITLE is set and DOPTION is \"colz\".")
      ("flip", "Flip the geometry/data histograms vertically. This option does not filp the y-axis, so that the y-coordinates in the flipped data will not correspond to those in the original histogram. An advantage of this is that the user can zoom the y-range with the mouse.")
      ("flipwithaxis", "Same as the 'flip' option but the y-axis is also flipped with drawback that the mouse zoom along the y-axis does not work.")
      //      ("bgcolor", "Set the frame background colour to some hard-coded value")
      ("o", po::value<std::string>()->default_value(""),
       "Output file name. If given then the canvas is not shown.")
       ("slice", po::value<std::vector<unsigned short> >()->multitoken()->default_value(std::vector<unsigned short>({0}),
                                                                             "no slice"),
       "Show live slice averaging the given number of bins. "
       "Left mouse click on the 2D histogram swaps axes, middle button click swaps logy. "
       "Two integer numbers are required: the first one is the number of bins "
       "to average the slice on 2D histogrm, the second one indicates how many bins "
       "of this have to be merged into one bin in the 1D histogram.")
      ("errors", "Plot the histogram with relative errors instead of data. This option is not compatible with -maxerror.")
      ("max","Plot the histogram where each bin content is the max value "
       "of all histograms along the normal axis. In order to avoid statistically unsignificant outliers (causing single-particle tracks in the max plots), "
       "the bin value is compared with the max value at the 1 sigma level: bin-ebin < max+emax, see the Data3::BuildMaxH2() method. "
       "With this option the '-offset' value applies to geomtry only which allows to select "
       "the representative geometry view.")
      ("maxerror",po::value<double>()->default_value(-1.0),
       "Bins with relative error above this value will not be shown. With negative value (by default) the bin error is not checked, i.e. all bins are drawn. This option is not compatible with -errors.")
      ("palette",po::value<std::string>()->default_value("MAXIV"),"Set colour palette. ROOT palette names predefined in TColor::EColorPalette are alowed, e.g. kDeepSea."
       " Palette can be inverted if preceeded by a minus sign, e.g. -kDeepSea.")
      ("v", "Explain what is being done.");

    po::options_description data("Data options", w.ws_col);
    data.add_options()
      ("scale", po::value<float>()->default_value(1.0), "Data scaling factor")
      ("doption", po::value<std::string>()->default_value("colz"), "Data draw option")
      ("dcont", po::value<size_t>()->default_value(200), "Number of contour levels for data")
      ("no-logz", "Remove log scale for the data colour axis");

    po::options_description geom("Geometry options", w.ws_col);
    geom.add_options()
      ("goption", po::value<std::string>()->default_value("cont3"), "Geometry draw option")
      ("gcont", po::value<size_t>()->default_value(25), "Number of contour levels for geometry")
      ("glwidth", po::value<size_t>()->default_value(2), "Geometry line width")
      ("glcolor", po::value<std::string>()->default_value("#000000"), "Geometry line colour specified by hex code, e.g. \"#rrggbb\"")
      ("glalpha", po::value<float>()->default_value(0.4), "Geometry line transparency");

    std::array<std::string, 4> positional_args{"dfile", "dhist", "gfile", "ghist"};
    po::positional_options_description p;
    for (const std::string& pa : positional_args)
      p.add(pa.data(), 1);

    po::options_description all_options("Usage: hplot [options] dfile dhist [gfile [ghist]]");
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
	if ((it == parsed.options.end()) && (pa!="gfile") && (pa!="ghist") ) // gfile and ghist are optional
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

    errors = vm.count("errors");

    if (errors && (IsMaxErr()))
      {
	std::cerr << "Error: -errors and -maxerror can not be used together" << std::endl;
	exit(1);
      }

    if (GetMaxErr()>1.0)
      {
	std::cerr << "Error: -maxerror must be <= 1.0" << std::endl;
	exit(1);
      }


    if (help || vm.count("help"))
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
    std::cerr << "hplot ERROR: " << e.what() << "\n";
    exit(1);
  }
  catch(...) {
    std::cerr << "Exception of unknown type!\n";
    exit(2);
  }

  return;
}

bool Arguments::IsBatch() const
{
  return !vm["o"].as<std::string>().empty();
}

bool Arguments::test() const
{
  const float xmin = vm["xmin"].as<float>();
  const float xmax = vm["xmax"].as<float>();
  const float ymin = vm["ymin"].as<float>();
  const float ymax = vm["ymax"].as<float>();

  bool val = CheckMinMax(xmin, xmax, "x") && CheckMinMax(ymin, ymax, "y");

  val = val & CheckSlice();

  const std::string offset = GetOffset();
  try {
    std::stof(offset);
  }
  catch (std::invalid_argument const &e) {
    if ((offset != "centre") && (offset != "min") && (offset != "max")) {
      std::cerr << "Arguments::test(): unknown 'offset' value: " << offset << std::endl;
      val = false;
    }
  }

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
  const std::vector<unsigned short> slice = GetSlice();
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
  const std::string title = "hplot: " + vm["dfile"].as<std::string>() + " " +
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
  const std::vector<unsigned short> slice = GetSlice();

  return (!((slice.size() == 1) && (slice[0] == 0)));
}

bool Arguments::IsZTitle() const
/*!
  Return true if z-title is shown
  (and therefore canvas right margin should be set)
 */
{
  return ((GetZTitle() != "None") && (!GetZTitle().empty()) &&
	  (GetDoption() == "colz")) || IsErrors();
}

bool Arguments::IsMaxErr(const double& val, const double& err) const
/*!
  Return true if err/val < GetMaxErr()
*/
{
  //  std::cout << IsMaxErr() << " " << (err/val<GetMaxErr()) << std::endl;

  if (!IsMaxErr())
    return true;
  else if (val==0.0)
    return false;
  else if (err/val<GetMaxErr())
    return true;
  else
    return false;
}
