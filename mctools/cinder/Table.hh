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

				  Table(string,int);
				  Table() {};
				 ~Table() {};

			   void   setName(string);
			   void   setNumber(int);

			   void   addBeamState(bool);
			   void   addTimeStep(double);

			    int   addNuclide(Nuclide);

			    int   findNuclide(string);
			   void   listNuclides();
			   void   listNuclides(string);

			 string   getName();
			    int   getNumber();

			Nuclide  *getNuclide(int);

			    int   getNNuclides();
			    int   getNBeamStates();

		 vector<double>   getTimeSteps();
		   vector<bool>   getBeamStates();

			   void   getMostActive(double, int timeStep = -1); // Set the threshold (%) over which the
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
			    int   tableNumber;

		   vector<bool>   beamStates;
		 vector<double>   timeSteps;

		vector<Nuclide>   Nuclides;

		 vector<double>   totalActivity;


	ClassDef(Table,1);

};

#endif

