#ifndef Data_h_
#define Data_h_

#include <TH3F.h>
#include <TH2F.h>
#include <TAxis.h>

class Data {
 private:
  TH3F *h3;
  TH2F *h2;
  std::string plane;
  TAxis *GetAxis() const;
  TH2F  *Project();
 public:
  Data(const TH3F *h3,
       const std::string& plane);
  Data(const std::string& fname,
       const std::string& hname,
       const std::string& plane);
  virtual ~Data();
  const TH3F* GetH3() const { return h3; };
  TH2F* GetH2() const { return h2; };

};


#endif
