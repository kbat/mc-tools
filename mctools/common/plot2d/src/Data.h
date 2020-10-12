#ifndef Data_h_
#define Data_h_

#include <TH3F.h>
#include <TH2F.h>
#include <TAxis.h>

#include "Arguments.h"

class Data {
 private:
  std::shared_ptr<TH3F> h3;
  std::shared_ptr<TH2F> h2;
  std::string plane;
  Arguments *args;
  TAxis *GetAxis() const;
  std::shared_ptr<TH2F> Project();
 public:
  /* Data(const TH3F* h3, */
  /*      const std::string& plane); */
  Data(const std::string& fname,
       const std::string& hname,
       const Arguments *args);
  virtual ~Data();
  const std::shared_ptr<TH3F> GetH3() const { return h3; };
  std::shared_ptr <TH2F> GetH2() const { return h2; };
};


#endif
