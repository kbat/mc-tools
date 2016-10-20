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

                           void   setName(string);
                           void   setNumber(Int_t);

                           void   addBeamState(Bool_t);
                           void   addTimeStep(Double_t);

                        ULong_t   addNuclide(TNuclide);

                          Int_t   findNuclide(string);
                           void   listNuclides();
                           void   listNuclides(string);

                         string   getName() const;
                          Int_t   getNumber() const;

                       TNuclide  *getNuclide(Int_t);

                        ULong_t   getNNuclides() const;
                        ULong_t   getNBeamStates() const;

               vector<Double_t>   getTotalActivity();

               vector<Double_t>   getTimeSteps() const;
                 vector<Bool_t>   getBeamStates() const;

                           void   getMostActive(Double_t, Int_t timeStep = -1); // Set the threshold (%) over which the
                                                                                // the activity is considered significative.
                                                                                // Optionally, the desired time step can be
                                                                                // selected, otherwise the complete list will
                                                                                // be produced.

                           void   finalizeTable();

        private:

                           void   calculateTotals();
                           void   toPercent();

        private:

                         string   tableName;
                          Int_t   tableNumber;

                 vector<Bool_t>   beamStates;
               vector<Double_t>   timeSteps;

               vector<TNuclide>   Nuclides;

               vector<Double_t>   totalActivity;


        ClassDef(TTable,1);

};

#endif

