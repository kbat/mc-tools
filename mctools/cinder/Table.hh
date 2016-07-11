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

			    int   findNuclide(string n);
			   void   listNuclides();
			   void   listNuclides(string n);

			 string   getName();
			    int   getNumber();

			Nuclide  *getNuclide(int);

			    int   getNNuclides();
			    int   getNBeamStates();

		 vector<double>   getTimeSteps();
		   vector<bool>   getBeamStates();

			   void   getMostActive(); // Activities sorted in descending order
						   // for all nuclides at all the time steps
			   void   getMostActive(int); // Set the maximum number of displayed nuclides
			   void   getMostActive(double); // Set the activity rejection threshold (%).
							 // Only nuclides with activity >= than threshold
							 // will be displayed

			   void   finalizeTable();

	private:

			   void   calculateTotals();

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

