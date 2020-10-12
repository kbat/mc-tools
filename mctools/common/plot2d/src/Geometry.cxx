#include "Geometry.h"

Geometry::Geometry(const std::string& fname, const std::string& hname,
		   const Arguments *args) : Data(fname, hname, args)
{
  std::cout << "Geometry constructor" << std::endl;
}

Geometry::~Geometry()
{

}
