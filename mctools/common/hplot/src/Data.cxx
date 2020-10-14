#include <iostream>
#include <chrono>
#include <TFile.h>
#include "Data.h"

// Data::Data(const TH3* h3, const std::string& plane) :
//   h3(h3), h2(nullptr), plane(plane)
// {
//   // std::cout << "Data constructor" << std::endl;
//   // h3->Print();
// }

Data::Data(const std::string& fname, const std::string& hname,
	   const Arguments *args) :
  h3(nullptr), plane(""), h2(nullptr), args(args)
{
  plane = args->GetPlane();
  TFile df(fname.c_str());
  if (df.IsZombie()) {
    df.Close();
    exit(1);
  }
  TH3 *h3tmp(nullptr);
  df.GetObject<TH3>(hname.c_str(),h3tmp);
  if (!h3tmp) {
    std::cerr << "Error: Can't find " << hname << " in " << fname << std::endl;
    exit(1);
  }

  h3 = std::shared_ptr<TH3>(static_cast<TH3*>(h3tmp));
  h3->SetDirectory(0);
  df.Close();

  h3tmp = nullptr;

  auto start = std::chrono::high_resolution_clock::now();
  h2 = Project();
  auto delta = std::chrono::high_resolution_clock::now()-start;
  std::cout << " Data::Project: " << std::chrono::duration_cast<std::chrono::milliseconds>(delta).count() << " ms" << std::endl;
  h2->Scale(args->GetScale());

  centre = args->GetCentre();
}

void Data::SetH2()
{
  if (args->GetTitle() != "None")
    h2->SetTitle(args->GetTitle().c_str());
  else
    h2->SetTitle(Form("%s: %s plane", h3->GetTitle(), plane.c_str()));

  if (args->GetXTitle() != "None")
     h2->SetXTitle(args->GetXTitle().c_str());
  else
    h2->SetXTitle(GetHorizontalAxis()->GetTitle());

  if (args->GetYTitle() != "None")
    h2->SetYTitle(args->GetYTitle().c_str());
  else
    h2->SetYTitle(GetVerticalAxis()->GetTitle());

  if (args->GetZTitle() != "None")
    h2->SetZTitle(args->GetZTitle().c_str());

  h2->SetContour(args->GetMap()["dcont"].as<size_t>());
  h2->SetOption(args->GetDoption().c_str());

  return;
}

Data::~Data()
{

}

TAxis *Data::GetNormalAxis() const
{
  /*!
    Return the plane normal axis
   */

  if (plane.find("x")==std::string::npos)
    return h3->GetXaxis();
  else if (plane.find("y")==std::string::npos)
    return h3->GetYaxis();
  else if (plane.find("z")==std::string::npos)
    return h3->GetZaxis();
  else {
    std::cerr << "Error: wrong plane " << plane << std::endl;
    return nullptr;
  }
}

TAxis *Data::GetHorizontalAxis() const
{
  if (plane[1] == 'x')
    return h3->GetXaxis();
  else if (plane[1] == 'y')
    return h3->GetYaxis();
  else if (plane[1] == 'z')
    return h3->GetZaxis();
  else
    {
      std::cerr << "Error in Data::GetHorizontalAxis()" << std::endl;
      return nullptr;
    }
}

TAxis *Data::GetVerticalAxis() const
{
  if (plane[0] == 'x')
    return h3->GetXaxis();
  else if (plane[0] == 'y')
    return h3->GetYaxis();
  else if (plane[0] == 'z')
    return h3->GetZaxis();
  else
    {
      std::cerr << "Error in Data::GetVerticalAxis()" << std::endl;
      return nullptr;
    }
}

std::shared_ptr<TH2> Data::Project()
{
  TAxis *a = GetNormalAxis();
  Int_t bin = a->FindBin(centre); // bin of the plane
  std::cout << "centre: " << centre << " cm,\tbin: "  << bin << std::endl;

  Float_t xmin = GetVerticalAxis()->GetXmin();
  Float_t xmax = GetVerticalAxis()->GetXmax();
  Float_t ymin = GetHorizontalAxis()->GetXmin();
  Float_t ymax = GetHorizontalAxis()->GetXmax();
  Int_t nx = GetVerticalAxis()->GetNbins();
  Int_t ny = GetHorizontalAxis()->GetNbins();

  const char *h2name = Form("%s_h2", h3->GetName());

  if (h3->IsA() == TH3F::Class()) // data
    h2 = std::make_shared<TH2F>(h2name, "h2 data title",     ny, ymin, ymax, nx, xmin, xmax);
  else if (h3->IsA() == TH3S::Class()) // geometry
    h2 = std::make_shared<TH2S>(h2name, "h2 geometry title", ny, ymin, ymax, nx, xmin, xmax);
  else if (h3->IsA() == TH3I::Class()) // geometry
    h2 = std::make_shared<TH2I>(h2name, "h2 geometry title", ny, ymin, ymax, nx, xmin, xmax);
  Float_t val, err;
  for (Int_t i=1; i<=ny; ++i)
    for (Int_t j=1; j<=nx; ++j) {
      val = h3->GetBinContent(j,i,bin);
      err = h3->GetBinError(j,i,bin);
      h2->SetBinContent(i,j,val);
      h2->SetBinError(i,j,err);
    }

  return h2;
}
