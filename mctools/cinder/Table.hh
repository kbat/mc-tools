#ifndef TABLE_HH
#define TABLE_HH

#include <string.h>
#include <cstdlib>
#include <vector>
#include <iostream>

#include <TObject.h>

#include "Nuclide.hh"

using namespace std;

class Table : public TObject {

	public:

				  Table(string,Int_t);
				  Table() {};
				 ~Table() {};

			   void   setName(string);
			   void   setNumber(Int_t);

			   void   addBeamState(Bool_t);
			   void   addTimeStep(Double_t);

			ULong_t   addNuclide(Nuclide);

			  Int_t   findNuclide(string);
			   void   listNuclides();
			   void   listNuclides(string);

			 string   getName();
			  Int_t   getNumber();

			Nuclide  *getNuclide(Int_t);

			ULong_t   getNNuclides();
			ULong_t   getNBeamStates();

	       vector<Double_t>   getTimeSteps();
		 vector<Bool_t>   getBeamStates();

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

		vector<Nuclide>   Nuclides;

	       vector<Double_t>   totalActivity;


	ClassDef(Table,1);

};

#endif

