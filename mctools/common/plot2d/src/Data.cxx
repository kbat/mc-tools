#include <iostream>
#include <chrono>
#include <TFile.h>
#include "Data.h"

// Data::Data(const TH3F* h3, const std::string& plane) :
//   h3(h3), h2(nullptr), plane(plane)
// {
//   // std::cout << "Data constructor" << std::endl;
//   // h3->Print();
// }

Data::Data(const std::string& fname, const std::string& hname,
	   const Arguments *args) :
  h3(nullptr), h2(nullptr), plane("")
{
  args=args;
  plane = args->GetPlane();
  TFile df(fname.c_str());
  if (df.IsZombie()) {
    df.Close();
    exit(1);
  }
  TH3F *h3tmp(nullptr);
  df.GetObject<TH3F>(hname.c_str(),h3tmp);
  if (!h3tmp) {
    std::cerr << "Error: Can't find " << hname << " in " << fname << std::endl;
    exit(1);
  }

  h3 = std::shared_ptr<TH3F>(static_cast<TH3F*>(h3tmp));
  h3->SetDirectory(0);
  df.Close();

  h3tmp = nullptr;

  auto start = std::chrono::high_resolution_clock::now();
  h2 = Project();
  auto delta = std::chrono::high_resolution_clock::now()-start;
  std::cout << " Data::Project (ms) " << std::chrono::duration_cast<std::chrono::milliseconds>(delta).count() << std::endl;
  h2->Scale(args->GetScale());

  if (args->GetTitle() != "None")
    h2->SetTitle(args->GetTitle().c_str());

  if (args->GetXTitle() != "None")
     h2->SetXTitle(args->GetXTitle().c_str());

  if (args->GetYTitle() != "None")
    h2->SetYTitle(args->GetYTitle().c_str());

  if (args->GetZTitle() != "None")
    h2->SetZTitle(args->GetZTitle().c_str());
}

Data::~Data()
{

}

TAxis *Data::GetAxis() const
{
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

std::shared_ptr<TH2F> Data::Project()
{
  TAxis *a = GetAxis();
  Double_t centre = 0.0;
  Int_t bin = a->FindBin(centre); // bin of the plane
  std::cout << bin << std::endl;

  Float_t xmin = h3->GetXaxis()->GetXmin();
  Float_t xmax = h3->GetXaxis()->GetXmax();
  Float_t ymin = h3->GetYaxis()->GetXmin();
  Float_t ymax = h3->GetYaxis()->GetXmax();
  Int_t nx = h3->GetNbinsX();
  Int_t ny = h3->GetNbinsY();
  h2 = std::make_shared<TH2F>("h2", "h2 title", ny, ymin, ymax, nx, xmin, xmax);
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
