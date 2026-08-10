#ifndef Application_h_
#define Application_h_

#include <memory>

#include <TCanvas.h>
#include <TApplication.h>

#include "Arguments.h"
#include "Data3.h"
#include "Geometry.h"
#include "MainFrame.h"

/*!
  Reads the data and the geometry and shows them, either in a window or - if
  an output file was given with -o - by printing a canvas and exiting.
*/
class Application {
 private:
  const std::shared_ptr<Arguments> args;
  std::shared_ptr<Data3> data;
  std::shared_ptr<Geometry> geo;

  // these must be raw pointers because ROOT collects them itself
  TCanvas *canvas;
  TApplication *theApp;

  std::unique_ptr<MainFrame> mf;

  TVirtualPad *SetUpCanvas(int& argc, const char **argv);
  void Print();

 public:
  explicit Application(const std::shared_ptr<Arguments>& args);

  /// Draw everything and either print the canvas or enter the event loop
  int Run(int& argc, const char **argv);
};

#endif
