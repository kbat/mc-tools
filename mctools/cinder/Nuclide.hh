#ifndef NUCLIDE_HH
#define NUCLIDE_HH

#include <string.h>
#include <cstdlib>
#include <vector>

#include <TObject.h>

using namespace std;

class Nuclide : public TObject {

	public:

				 Nuclide(string,double);
				 Nuclide() {};
				~Nuclide() {};

			  void   setName(string);
			  void   setHalflife(double);

			  void   addActivity(double);

			string   getName();
			  bool   getExcited();

			   int   getNActivity();
		vector<double>   getActivity();

			  void   trimActivity(int);

	private:

			  void   setExcited();

	private:

			string   nuclideName;
			double   halfLife;

			  bool   isExcited;

		vector<double>   activity;


	ClassDef(Nuclide,1);

};

#endif

