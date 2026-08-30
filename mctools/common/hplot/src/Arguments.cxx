#include <algorithm>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <sys/ioctl.h>

#include <TStyle.h>

#include "Arguments.h"
#include "Error.h"

Arguments::Arguments(int ac, const char **av) :
  help(false)
{
  const Plane xy("xy");
  // GetHeight() derives the height from the width when it is left at zero
  constexpr size_t unset_height = 0;

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
      ("gfile", po::value<std::string>()->default_value(""),
       "Geometry: the FLUKA, MCNP or PHITS input file to cut. If no file of that name exists, "
       "the name without its extension is taken to be the name of a TMacro holding the input "
       "file inside dfile - the copy fluka2root writes there.");

    po::options_description generic("Generic options", w.ws_col);
    generic.add_options()
      ("help,h", "Show this help message and exit.")
      ("plane", po::value<Plane>()->default_value(xy, "xy"),
       "Projection plane. Allowed values: xy, xz, yx, yz, zx, zy. The ROOT notation is used, i.e. the first symbol corresponds to the verical axis and the second symbol - to the horizontal axis of TH2.")
      ("offset", po::value<std::string>()->default_value("0.0"),
       "This parameter specifies the offset of the projection plane from the origin. "
       "It can be defined as a float number or as the strings 'min', 'max', or 'centre'. "
       "When 'centre' is used, the offset is set to the midpoint between the 'min' and 'max' values. "
       "If 'min' is used, the offset corresponds to the center of the first bin of the axis that is perpendicular to the projection plane, "
       "while 'max' corresponds to the last bin of that axis. "
       "When the '-max' option is used, the offset applies to the geometry only, "
       "which allows the selection of the representative geometry view.")
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
      ("height", po::value<size_t>()->default_value(unset_height),
       "Canvas height. If not specified, it is calculated from the width with the golden ratio rule.")
      ("rebin", "Rebin the 2D histograms such that they are not larger than the area they are "
       "drawn in - the canvas (see the width and height arguments) less the margins around the plot "
       "and, with the slice option, the pad the projection takes. This argument drastically speeds "
       "up histogram drawing, which costs one box per bin: a bin smaller than a pixel is paid for "
       "and not seen. Bins are merged in groups that divide the axis exactly where such a group "
       "size can be found, because whatever does not make up a whole group is dropped from the end "
       "of the axis; -v reports it when that happens.")
      ("right_margin", po::value<float>()->default_value(0.12),
       "Right margin of the canvas in order to allocate enough space for the TH2 z-axis title. "
       "Used only if ZTITLE is set and DOPTION is \"colz\".")
      ("flip", "Flip the data and the geometry vertically. This option does not filp the y-axis, so that the y-coordinates in the flipped data will not correspond to those in the original histogram. An advantage of this is that the user can zoom the y-range with the mouse.")
      ("flipwithaxis", "Same as the 'flip' option but the y-axis is also flipped with drawback that the mouse zoom along the y-axis does not work.")
      //      ("bgcolor", "Set the frame background colour to some hard-coded value")
      ("o", po::value<std::string>()->default_value(""),
       "Output file name. If given then the canvas is not shown.")
       ("slice", po::value<std::vector<unsigned short> >()->multitoken()->default_value(std::vector<unsigned short>({0}),
                                                                             "no slice"),
       "Show live slice averaging the given number of bins. "
       "Left mouse click on the 2D histogram swaps axes, middle button click swaps logy. "
       "Two integer numbers are required: the first one is the number of bins "
       "to average the slice on 2D histogram, the second one indicates how many bins "
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
      ("gres", po::value<size_t>()->default_value(1000),
       "Number of geometry samples across the horizontal axis. The vertical axis gets as many "
       "as the canvas aspect ratio calls for, so that the sampling is uniform in the picture. "
       "A boundary thinner than a sample cell can be missed, and the time the cut takes grows "
       "with the square of this number.")
      ("glwidth", po::value<size_t>()->default_value(2), "Geometry line width")
      ("glcolor", po::value<std::string>()->default_value("#000000"), "Geometry line colour specified by hex code, e.g. \"#rrggbb\"")
      ("glalpha", po::value<float>()->default_value(0.4), "Geometry line transparency");

    std::array<std::string, 3> positional_args{"dfile", "dhist", "gfile"};
    po::positional_options_description p;
    for (const std::string& pa : positional_args)
      p.add(pa.data(), 1);

    po::options_description all_options("Usage: hplot [options] dfile dhist [gfile]");
    all_options.add(generic).add(data).add(geom).add(hidden);

    //    po::store(po::parse_command_line(argc, argv, desc), vm);
    auto parsed = po::command_line_parser(ac, av).options(all_options).positional(p)
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

    // an explicit -h must not complain about the missing positional arguments
    help = std::any_of(parsed.options.begin(), parsed.options.end(),
		       [](po::option const& o) { return o.string_key == "help"; });

    if (!help)
      for (const std::string& pa : positional_args)
	{
	  auto it = std::find_if(parsed.options.begin(), parsed.options.end(),
				 [&pa](po::option const& o) {
				   return o.string_key == pa;
				 });
	  if ((it == parsed.options.end()) && (pa!="gfile")) // gfile is optional
	    {
	      std::cerr << "Error: Missing positional argument \"" <<
		pa << "\"\n" << std::endl;
	      help=true;
	      break;
	    }
	}

    po::store(parsed, vm);
    po::notify(vm);

    Cache();

    if (help)
      {
	std::stringstream stream;
	stream << all_options;
	std::string helpMsg = stream.str();
	boost::algorithm::replace_all(helpMsg, "--", "-");
	boost::algorithm::replace_all(helpMsg, "-dfile", " dfile");
	boost::algorithm::replace_all(helpMsg, "-dhist", " dhist");
	boost::algorithm::replace_all(helpMsg, "-gfile", " gfile");
	std::cout << helpMsg << std::endl;
	return;
      }
  }
  catch(const po::error& e) {
    throw HPlotError(e.what());
  }

  // these need the parsed values, so they run outside the block above
  if (IsErrors() && IsMaxErr())
    throw HPlotError("-errors and -maxerror can not be used together");

  if (GetMaxErr()>1.0)
    throw HPlotError("-maxerror must be <= 1.0");

  return;
}

void Arguments::Cache()
/*!
  Read the options that are asked for again and again, now that the command
  line has been parsed.

  Order matters only in that ztitle is derived from two of the others.
 */
{
  hot.batch       = !GetOutputFile().empty();
  hot.errors      = vm.count("errors");
  hot.flippedaxis = vm.count("flipwithaxis");
  hot.flipped     = vm.count("flip") || hot.flippedaxis;
  hot.logz        = !vm.count("no-logz");
  hot.max         = vm.count("max");
  hot.rebin       = vm.count("rebin");
  hot.verbose     = vm.count("v");
  hot.maxerr      = vm["maxerror"].as<double>();

  // the default is the single element 0, which means the option was not given
  const std::vector<unsigned short>& slice = GetSlice();
  hot.slice = !((slice.size() == 1) && (slice[0] == 0));

  hot.height = vm["height"].as<size_t>();
  if (hot.height == 0) {
    constexpr float sqrt5 = 2.236068;
    hot.height = round(GetWidth()*2.0/(1.0+sqrt5)); // golden ratio
  }

  /*
    The z axis title needs room on the right of the canvas, and -errors puts
    one there whether the user asked for it or not - see ErrorHist().
  */
  hot.ztitle = ((GetZTitle() != "None") && (!GetZTitle().empty()) &&
		(GetDoption() == "colz")) || hot.errors;

  /*
    The pad the data are drawn in.  Application::SetUpCanvas() divides the
    canvas in two when the live slice is shown, and TPad::Divide() leaves
    divideMargin around each of the pads it makes.
  */
  const bool divided = hot.slice && !hot.batch;
  const double padw = divided ? 1.0 - 2*divideMargin : 1.0;
  const double padh = divided ? 0.5 - 2*divideMargin : 1.0;

  /*
    And the frame inside that pad, which is the pad less its margins.  The
    wider right margin -ztitle asks for is set on the canvas, so it only
    reaches the plot while the canvas is the plot's own pad.
  */
  const double left   = gStyle->GetPadLeftMargin();
  const double top    = gStyle->GetPadTopMargin();
  const double bottom = gStyle->GetPadBottomMargin();
  const double right  = (hot.ztitle && !divided) ? GetRightMargin()
                                                 : gStyle->GetPadRightMargin();

  hot.plotwidth  = std::max<size_t>(1, std::lround(GetWidth()*padw*(1.0-left-right)));
  hot.plotheight = std::max<size_t>(1, std::lround(hot.height*padh*(1.0-top-bottom)));
}

bool Arguments::test() const
{
  bool val = CheckMinMax(GetXmin(), GetXmax(), "x") &&
             CheckMinMax(GetYmin(), GetYmax(), "y");

  val = val & CheckSlice();

  /*
    The names first, so that std::stof() is asked only about something that is
    meant to be a number - and so that a number too large for a float is
    reported here rather than thrown out of this function, which is how
    -offset 1e400 used to leave hplot saying nothing but "stof".
    Data3::GetOffset() reads the value the same way round.
  */
  const std::string offset = GetOffset();
  if ((offset != "centre") && (offset != "min") && (offset != "max")) {
    try {
      std::stof(offset);
    }
    catch (const std::invalid_argument&) {
      std::cerr << "Arguments::test(): 'offset' is neither a number nor one of "
	"centre, min, max: " << offset << std::endl;
      val = false;
    }
    catch (const std::out_of_range&) {
      std::cerr << "Arguments::test(): 'offset' is out of the range of a float: "
		<< offset << std::endl;
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
  const std::vector<unsigned short>& slice = GetSlice();
  const size_t size = slice.size();

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
  const std::string title = "hplot: " + GetDataFile() + " " +
    GetDataHist() + " " + GetPlane().GetValue();

  return title;
}

bool Arguments::IsMaxErr(const double& val, const double& err) const
/*!
  Return true if err/val < GetMaxErr()

  The rule itself lives in MaxErr, which is what the projection loops use - so
  that it is written down once, and so that they do not pay for the option
  lookup this convenience wrapper does.
*/
{
  return MaxErr(*this)(val, err);
}
