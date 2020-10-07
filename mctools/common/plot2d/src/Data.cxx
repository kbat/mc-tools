#include <iostream>
#include <chrono>
#include <TFile.h>
#include "Data.h"

Data::Data(const TH3F *h3, const std::string& plane) :
  h3(const_cast<TH3F*>(h3)), h2(nullptr), plane(plane)
{
  // std::cout << "Data constructor" << std::endl;
  // h3->Print();
}

Data::Data(const std::string& fname, const std::string& hname,
	   const std::string& plane) :
  h3(nullptr), h2(nullptr), plane(plane)
{
  TFile df(fname.c_str());
  if (df.IsZombie()) {
    df.Close();
    exit(1);
  }

  df.GetObject<TH3F>(hname.c_str(),h3);
  if (!h3) {
    std::cerr << "Error: Can't find " << hname << " in " << fname << std::endl;
    df.Close();
    exit(1);
  }
  h3->SetDirectory(0);
  df.Close();
  auto start = std::chrono::high_resolution_clock::now();
  h2 = Project();
  auto delta = std::chrono::high_resolution_clock::now()-start;
  std::cout << " Data::Project (ms) " << std::chrono::duration_cast<std::chrono::milliseconds>(delta).count() << std::endl;
}

Data::~Data()
{
  std::cout << "Data: desctructor" << std::endl;
  if (h2)
    h2->Delete();
  if (h3)
    h3->Delete();
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

TH2F *Data::Project()
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
  h2 = new TH2F("h2", "h2 title", ny, ymin, ymax, nx, xmin, xmax);
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

// Data::~Data()
// {
//   h2->Delete();
// }
