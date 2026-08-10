#include <iostream>
#include <memory>

#include "Application.h"
#include "Arguments.h"
#include "Error.h"

int main(int argc, const char **argv)
{
  try
    {
      std::shared_ptr<Arguments> args = std::make_shared<Arguments>(argc, argv);

      if (args->IsHelp())
	return 0;

      if (!args->test())
	return 1;

      Application app(args);

      return app.Run(argc, argv);
    }
  catch (const std::exception& e)
    {
      std::cerr << "hplot: " << e.what() << std::endl;
      return 1;
    }
}
