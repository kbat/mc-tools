#include <iostream>

#include "TList.h"
#include "TGraph.h"
#include "TColor.h"

#include "Chrono.h"
#include "GeometryMultiGraph.h"

GeometryMultiGraph::GeometryMultiGraph(TMultiGraph *mg,
				       const std::shared_ptr<Arguments> args,
				       const std::shared_ptr<Data3> d) :
  mg(mg), data(d)
{
  const Int_t col = TColor::GetColor(args->GetGlcolor().data());
  const Float_t alpha = args->GetGlalpha();

  TGraph *obj(nullptr);
  const TList *l = mg->GetListOfGraphs();
  TIter next(l);
  while ((obj = dynamic_cast<TGraph*>(next())))
    {
      obj->SetLineWidth(args->GetGlwidth());
      obj->SetLineColorAlpha(col, alpha);
      obj->SetMarkerColorAlpha(col, alpha);
    }

  if (args->IsFlipped())
    {
      Chrono t(args->IsVerbose(), " GeometryMultiGraph::Flip");
      Flip();
    }
}

void GeometryMultiGraph::Draw()
{
  mg->Draw("l");
}

std::string GeometryMultiGraph::StatusText(Double_t x, Double_t y) const
{
  (void)x; (void)y;
  return "Geometry: PLOTGEOM";
}

void GeometryMultiGraph::Flip()
{
  const auto h3 = data->GetH3();
  const TAxis *a = GetAxis(*h3, data->GetPlane().Vertical());

  const Double_t offset = a->GetXmin() + a->GetXmax();

  TGraph *gr(nullptr);
  const TList *l = mg->GetListOfGraphs();
  TIter next(l);
  while ((gr = dynamic_cast<TGraph*>(next())))
    {
      const Int_t N = gr->GetN();
      for (Int_t i=0; i<N; ++i)
	{
	  const Double_t x = gr->GetX()[i];
	  const Double_t y = offset-gr->GetY()[i];
	  gr->SetPoint(i, x, y);
	}
    }
}
