#ifndef TTABLE_HH
#define TTABLE_HH

#include <string.h>
#include <cstdlib>
#include <vector>
#include <iostream>

#include <TObject.h>

#include "TNuclide.h"

using namespace std;

class TTable : public TObject {

        public:

                                  TTable(string,Int_t);
                                  TTable() {};
                                 ~TTable() {};

                           void   SetName(string);
                           void   SetNumber(Int_t);

                           void   AddBeamState(Bool_t);
                           void   AddTimeStep(Double_t);

                        ULong_t   AddNuclide(TNuclide);

                          Int_t   FindNuclide(string);
                           void   ListNuclides();
                           void   ListNuclides(string);

                     const char  *GetName() const;
                          Int_t   GetNumber() const;

                       TNuclide  *GetNuclide(Int_t);

                        ULong_t   GetNNuclides() const;
                        ULong_t   GetNBeamStates() const;

               vector<Double_t>   GetTotalActivity();

               vector<Double_t>   GetTimeSteps() const;
                 vector<Bool_t>   GetBeamStates() const;

                           void   GetMostActive(Double_t, Int_t timeStep = -1); // Set the threshold (%) over which the
                                                                                // the activity is considered significative.
                                                                                // Optionally, the desired time step can be
                                                                                // selected, otherwise the complete list will
                                                                                // be produced.

                           void   FinalizeTable();

        private:

                           void   CalculateTotals();
                           void   ToPercent();

        private:

                         string   fTableName;
                          Int_t   fTableNumber;

                 vector<Bool_t>   fBeamStates;
               vector<Double_t>   fTimeSteps;

               vector<TNuclide>   fNuclides;

               vector<Double_t>   fTotalActivity;


        ClassDef(TTable,1);

};

#endif

