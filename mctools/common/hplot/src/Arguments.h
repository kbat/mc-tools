#ifndef Arguments_h_
#define Arguments_h_

#include <limits>
#include <string>
#include <vector>

#include <boost/program_options.hpp>
#include <boost/algorithm/string/replace.hpp>

#include "Plane.h"

namespace po=boost::program_options;

/*!
  The command line.

  Every option is read through a typed accessor, so that the option names
  appear in this file only.
*/
class Arguments {
 private:
  po::variables_map vm;
  bool help;
  bool CheckMinMax(const float &vmin, const float &vmax, const std::string &title) const;
  bool CheckSlice() const;

 public:
  Arguments(int ac, const char **av);

  bool IsBatch() const;
  bool IsErrors() const { return vm.count("errors"); }
  bool IsFlipped() const { return vm.count("flip") || vm.count("flipwithaxis"); }
  bool IsFlippedAxis() const { return vm.count("flipwithaxis"); }
  bool IsHelp() const { return help; }
  bool IsLogz() const { return !vm.count("no-logz"); }
  bool IsMax() const { return vm.count("max"); }
  bool IsRebin() const { return vm.count("rebin"); }
  bool IsVerbose() const { return vm.count("v"); }
  bool  IsXmin() const { return GetXmin()>std::numeric_limits<float>::lowest(); }
  bool  IsXmax() const { return GetXmax()<std::numeric_limits<float>::max(); }
  bool  IsYmin() const { return GetYmin()>std::numeric_limits<float>::lowest(); }
  bool  IsYmax() const { return GetYmax()<std::numeric_limits<float>::max(); }
  bool  IsZmin() const { return GetZmin()>std::numeric_limits<float>::lowest(); }
  bool  IsZmax() const { return GetZmax()<std::numeric_limits<float>::max(); }
  bool  IsZTitle() const;
  bool        IsSlice() const;

  // positional arguments
  std::string GetDataFile() const { return vm["dfile"].as<std::string>(); }
  std::string GetDataHist() const { return vm["dhist"].as<std::string>(); }
  std::string GetGeoFile()  const { return vm["gfile"].as<std::string>(); }

  std::string GetOffset()  const { return vm["offset"].as<std::string>(); }
  size_t      GetHeight() const;
  Plane       GetPlane() const { return vm["plane"].as<Plane>(); }
  const std::vector<unsigned short>& GetSlice() const
  { return vm["slice"].as<std::vector<unsigned short> >(); }
  unsigned short GetSlice(size_t i) const { return GetSlice()[i]; }
  std::string GetTitle() const { return vm["title"].as<std::string>(); }
  size_t      GetWidth()  const { return vm["width"].as<size_t>(); }
  std::string GetWindowTitle() const;
  std::string GetXTitle() const { return vm["xtitle"].as<std::string>(); }
  std::string GetYTitle() const { return vm["ytitle"].as<std::string>(); }
  std::string GetZTitle() const { return vm["ztitle"].as<std::string>(); }
  float GetXmin() const { return vm["xmin"].as<float>(); }
  float GetXmax() const { return vm["xmax"].as<float>(); }
  float GetYmin() const { return vm["ymin"].as<float>(); }
  float GetYmax() const { return vm["ymax"].as<float>(); }
  float GetZmin() const { return vm["zmin"].as<float>(); }
  float GetZmax() const { return vm["zmax"].as<float>(); }
  float GetRightMargin() const { return vm["right_margin"].as<float>(); }
  std::string GetOutputFile() const { return vm["o"].as<std::string>(); }
  std::string GetPalette() const { return vm["palette"].as<std::string>(); }

  // data options
  std::string GetDoption() const { return vm["doption"].as<std::string>(); }
  size_t      GetDcont()   const { return vm["dcont"].as<size_t>(); }
  float       GetScale()   const { return vm["scale"].as<float>(); }

  // geometry options
  size_t      GetGres()    const { return vm["gres"].as<size_t>(); }
  size_t      GetGlwidth() const { return vm["glwidth"].as<size_t>(); }
  std::string GetGlcolor() const { return vm["glcolor"].as<std::string>(); }
  float       GetGlalpha() const { return vm["glalpha"].as<float>(); }

  inline double GetMaxErr() const { return vm["maxerror"].as<double>(); }
  inline bool   IsMaxErr()  const { return vm["maxerror"].as<double>()>0.0; }
  bool   IsMaxErr(const double&, const double&) const;
  bool test() const;
};

/*!
  The -maxerror cut, with the option already looked up.

  Arguments reads its options out of a map of boost::any, which is far too slow
  to do once per bin of a projection - and the projection loops run on worker
  threads, which have no business reaching into the command line at all.
*/
class MaxErr {
 private:
  double limit; ///< <= 0: every bin passes

 public:
  MaxErr() : limit(-1.0) {}
  explicit MaxErr(const Arguments& a) : limit(a.GetMaxErr()) {}

  bool operator()(double val, double err) const
  { return (limit<=0.0) || ((val!=0.0) && (err/val<limit)); }
};

#endif
