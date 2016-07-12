#ifndef NUCLIDE_HH
#define NUCLIDE_HH

#include <string.h>
#include <cstdlib>
#include <vector>
#include <iostream>

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
			double   getActivity(int);
			double   getPActivity(int);
		vector<double>   getActivities();

			  void   trimActivity(int);
			  void   calculatePercent(vector<double>);

	private:

			  void   setExcited();

	private:

			string   nuclideName;
			double   halfLife;

			  bool   isExcited;

		vector<double>   activity;
		vector<double>   pActivity;


	ClassDef(Nuclide,1);

};

#endif

