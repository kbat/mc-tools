#include "GeometryMultiGraph.h"
#include "TFile.h"
#include "TList.h"
#include "TGraph.h"
#include "TColor.h"
#include <iostream>

GeometryMultiGraph::GeometryMultiGraph(const std::string& fname, const std::string& mgname,
			       const std::shared_ptr<Arguments> args) :
  Geometry(fname,mgname,args)
{
  std::cout << "GeometryMultiGraph: constructor" << std::endl;

  TFile df(fname.data());
  if (df.IsZombie()) {
    df.Close();
    exit(1);
  }
  mg = df.Get<TMultiGraph>(mgname.data());
  df.Close();

  TGraph *obj(nullptr);
  const TList *l = mg->GetListOfGraphs();
  TIter next(l);
  while ((obj = dynamic_cast<TGraph*>(next())))
    {
      // move this to SetH2 as in Geometry3
      obj->SetLineWidth(args->GetMap()["glwidth"].as<size_t>());
      const Int_t col = TColor::GetColor(args->GetMap()["glcolor"].as<std::string>().data());
      obj->SetLineColor(col);
    }
}

void GeometryMultiGraph::Draw() const
{
  std::cout << "GeometryMultiGraph::Draw()" << std::endl;
  mg->Draw("pl");
}
