#ifndef TABLE_HH
#define TABLE_HH

#include <string.h>
#include <cstdlib>
#include <vector>

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
			Nuclide  *getNuclide(int);

			    int   getNNuclides();
			    int   getNBeamStates();

		 vector<double>   getTimeSteps();
		   vector<bool>   getBeamStates();

			   void   finalizeTable();

	private:

			 string   tableName;
			    int   tableNumber;

		   vector<bool>   beamStates;
		 vector<double>   timeSteps;

		vector<Nuclide>   Nuclides;


	ClassDef(Table,1);

};

#endif

