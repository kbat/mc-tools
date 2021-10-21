#include "Data.h"

Data::Data(const std::string& fname, const std::string& objname,
	   const std::shared_ptr<Arguments> args) :
  args(args)
{
}

void Data::PrintChrono(std::chrono::system_clock::time_point start, std::string msg) const
{
  if (args->IsVerbose())
    {
      auto delta = std::chrono::high_resolution_clock::now()-start;
      std::cout << msg << ": " << std::chrono::duration_cast<std::chrono::milliseconds>(delta).count() << " ms" << std::endl;
    }
}
