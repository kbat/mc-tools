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
  bool CheckMinMax(const float &vmin, const float &vmax, const std::string &title) const;
  bool CheckSlice() const;
 public:
  Arguments(int ac, const char **av);
  po::variables_map GetMap() const { return &vm; }
  bool IsBatch() const;
  bool IsHelp() const { return help; }
  bool IsLogz() const {return !vm.count("no-logz"); }
  bool        IsSlice() const;
  std::string GetOffset()  const { return vm["offset"].as<std::string>(); }
  std::string GetDoption() const {return vm["doption"].as<std::string>(); }
  std::string GetGoption() const {return vm["goption"].as<std::string>(); }
  size_t      GetHeight() const;
  std::string GetPlane() const {return vm["plane"].as<Plane>().GetValue(); }
  float       GetScale()  const { return vm["scale"].as<float>(); }
  std::vector<short> GetSlice() const { return vm["slice"].as<std::vector<short> >(); }
  size_t      GetSlice(size_t i) const { return GetSlice()[i]; }
  std::string GetTitle() const {return vm["title"].as<std::string>(); }
  size_t      GetWidth()  const { return vm["width"].as<size_t>(); }
  std::string GetWindowTitle() const;
  std::string GetXTitle() const {return vm["xtitle"].as<std::string>(); }
  std::string GetYTitle() const {return vm["ytitle"].as<std::string>(); }
  std::string GetZTitle() const {return vm["ztitle"].as<std::string>(); }
  float GetZMax() const {return vm["zmax"].as<float>(); }
  float GetZMin() const {return vm["zmin"].as<float>(); }
  bool test() const;
};

#endif
