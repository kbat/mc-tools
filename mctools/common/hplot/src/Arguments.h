#ifndef Arguments_h_
#define Arguments_h_

#include <iostream>
#include <limits>
#include <sys/ioctl.h>

#include <boost/program_options.hpp>
#include <boost/algorithm/string/replace.hpp>


namespace po=boost::program_options;

class Plane {
 private:
  std::string value;
 public:
 Plane(std::string const &val) :
  value(val)
    {
    }

  std::string GetValue() const { return value; }

  operator std::string() const
  {
    return value;
  }

  friend std::ostream& operator<<(std::ostream& os, const Plane& p)
  {
    os << p.value;
    return os;
  }
};

class Arguments {
 private:
  int argc;
  const char **argv;
  po::variables_map vm;
  bool help;
  bool errors; // true if called with -errors
  bool CheckMinMax(const float &vmin, const float &vmax, const std::string &title) const;
  bool CheckSlice() const;
 public:
  Arguments(int ac, const char **av);
  po::variables_map GetMap() const { return &vm; }
  bool IsBatch() const;
  bool IsErrors() const { return errors; }
  bool IsFlipped() const { return vm.count("flip"); }
  bool IsHelp() const { return help; }
  bool IsLogz() const { return !vm.count("no-logz"); }
  bool IsMax() const { return vm.count("max"); }
  bool IsRebin() const { return vm.count("rebin"); }
  bool IsVerbose() const { return vm.count("v"); }
  bool IsXmin() const { return GetXmin()>std::numeric_limits<float>::lowest(); }
  bool IsXmax() const { return GetXmax()<std::numeric_limits<float>::max(); }
  bool IsYmin() const { return GetYmin()>std::numeric_limits<float>::lowest(); }
  bool IsYmax() const { return GetYmax()<std::numeric_limits<float>::max(); }
  bool IsZmin() const { return GetZmin()>std::numeric_limits<float>::lowest(); }
  bool IsZmax() const { return GetZmax()<std::numeric_limits<float>::max(); }
  bool IsZTitle() const;
  bool IsSlice() const;
  bool IsProfile() const { return vm.count("profile"); }
  std::string GetOffset()  const { return vm["offset"].as<std::string>(); }
  std::string GetDoption() const { return vm["doption"].as<std::string>(); }
  std::string GetGoption() const { return vm["goption"].as<std::string>(); }
  size_t      GetHeight() const;
  std::string GetPlane() const { return vm["plane"].as<Plane>().GetValue(); }
  float       GetScale()  const { return vm["scale"].as<float>(); }
  std::vector<unsigned short> GetSlice() const { return vm["slice"].as<std::vector<unsigned short> >(); }
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
  inline double GetMaxErr() const { return vm["maxerror"].as<double>(); }
  inline bool   IsMaxErr()  const { return vm["maxerror"].as<double>()>0.0; }
  bool   IsMaxErr(const double&, const double&) const;
  std::string GetPalette() const { return vm["palette"].as<std::string>(); }
  bool test() const;
};

#endif
