#include "TColor.h"
#include "Geometry.h"

Geometry::Geometry(const std::string& fname, const std::string& hname,
		   const Arguments *args) : Data(fname, hname, args)
{

}

void Geometry::SetH2(std::shared_ptr<TH2> h2)
{
  h2->SetLineWidth(args->GetMap()["glwidth"].as<size_t>());

  const Int_t col = TColor::GetColor(args->GetMap()["glcolor"].as<std::string>().c_str());
  h2->SetLineColor(col);

  h2->SetContour(args->GetMap()["gcont"].as<size_t>());

  const std::string opt = "same " + args->GetMap()["goption"].as<std::string>();
  h2->SetOption(opt.c_str());

  return;
}

Geometry::~Geometry()
{
}
