#include "GeometryMultiGraph.h"
#include "TFile.h"
#include "TList.h"
#include "TGraph.h"
#include "TColor.h"
#include <iostream>

GeometryMultiGraph::GeometryMultiGraph(const std::string& fname, const std::string& mgname,
				       const std::shared_ptr<Arguments> args,
				       const std::shared_ptr<Data3> d) :
  Geometry(fname,mgname,args), data(d)
{
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

  if (args->IsFlipped())
    {
      //      auto start = std::chrono::high_resolution_clock::now();
      Flip();
      //      PrintChrono(start, " "+GetTypeStr()+"::Flip: ");
    }
}

void GeometryMultiGraph::Draw() const
{
  mg->Draw("pl");
}

void GeometryMultiGraph::Flip()
{
  const auto h3 = data->GetH3();
  const std::string plane = data->GetArgs()->GetPlane();
  TAxis *a(nullptr);

  if (plane[0] == 'x')
    a = h3->GetXaxis();
  else if (plane[0] == 'y')
    a = h3->GetYaxis();
  else
    a = h3->GetZaxis();

  const Double_t A = a->GetXmin();
  const Double_t B = a->GetXmax();
  const Double_t offset = A+B;

  TGraph *gr(nullptr);
  const TList *l = mg->GetListOfGraphs();
  TIter next(l);
  while ((gr = dynamic_cast<TGraph*>(next())))
    {
      const Int_t N = gr->GetN();
      for (Int_t i=0; i<N; ++i)
	{
	  const Double_t x = gr->GetX()[i];
	  const Double_t y = -gr->GetY()[i]+offset;
	  gr->SetPoint(i, x, y);
	}
    }
}
