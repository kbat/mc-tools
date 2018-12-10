#ifndef TNUCLIDE_HH
#define TNUCLIDE_HH

#include <string.h>
#include <cstdlib>
#include <vector>
#include <iostream>

#include <TObject.h>

using namespace std;

class TNuclide : public TObject {

        public:

                                 TNuclide(string,Double_t);
                                 TNuclide() {};
                                ~TNuclide() {};

                          void   SetName(string);
                          void   SetHalflife(Double_t);

                          void   AddActivity(Double_t);

                    const char  *GetName() const;
                        Bool_t   GetExcited() const;
                      Double_t   GetHalflife() const;

                       ULong_t   GetNActivity() const;
                      Double_t   GetActivity(Int_t) const;
                      Double_t   GetPActivity(Int_t) const;
              vector<Double_t>   GetActivities() const;

                          void   TrimActivity(Int_t);
                          void   CalculatePercent(vector<Double_t>);

        private:

                          void   SetExcited();

        private:

                        string   fNuclideName;
                      Double_t   fHalfLife;

                        Bool_t   fIsExcited;

              vector<Double_t>   fActivity;
              vector<Double_t>   fPActivity;


        ClassDef(TNuclide,1);

};

#endif

