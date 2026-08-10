#include <iostream>

#include <TFile.h>
#include <TH3.h>
#include <TMultiGraph.h>

#include "Chrono.h"
#include "Error.h"
#include "GeometryFactory.h"
#include "Geometry3.h"
#include "GeometryMultiGraph.h"

std::shared_ptr<Geometry> MakeGeometry(const std::shared_ptr<Arguments>& args,
				       const std::shared_ptr<Data3>& data)
{
  const std::string gfname = args->GetGeoFile();
  const std::string ghname = args->GetGeoHist();

  if (gfname.empty())
    return nullptr;

  TFile df(gfname.data());
  if (df.IsZombie()) {
    df.Close();
    throw HPlotError("can not open the geometry file " + gfname);
  }

  TObject *obj = df.Get<TObject>(ghname.data());
  if (!obj) {
    df.Close();
    throw HPlotError(ghname + " not found in " + gfname);
  }

  std::shared_ptr<Geometry> geo(nullptr);

  if (obj->InheritsFrom("TH3"))
    {
      TH3 *h3 = static_cast<TH3*>(obj);
      h3->SetDirectory(nullptr); // detach from the file we are about to close

      auto geo3 = std::make_shared<Geometry3>(h3, args);
      {
	Chrono t(args->IsVerbose(), "Geometry3::Project");
	geo3->Project();
      }
      data->Check(geo3->GetNormalAxis());

      geo = geo3;
    }
  else if (obj->InheritsFrom("TMultiGraph"))
    {
      geo = std::make_shared<GeometryMultiGraph>(static_cast<TMultiGraph*>(obj),
						 args, data);
    }
  else
    {
      const std::string cls = obj->ClassName();
      df.Close();
      throw HPlotError(ghname + " in " + gfname + " is a " + cls +
		       ", expected a TH3 or a TMultiGraph");
    }

  df.Close();

  return geo;
}
