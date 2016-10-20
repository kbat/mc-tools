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

			  void   setName(string);
			  void   setHalflife(Double_t);

			  void   addActivity(Double_t);

			string   getName();
			Bool_t   getExcited();
		      Double_t   getHalflife();

			 Int_t   getNActivity();
		      Double_t   getActivity(Int_t);
		      Double_t   getPActivity(Int_t);
	      vector<Double_t>   getActivities();

			  void   trimActivity(Int_t);
			  void   calculatePercent(vector<Double_t>);

	private:

			  void   setExcited();

	private:

			string   nuclideName;
		      Double_t   halfLife;

			Bool_t   isExcited;

	      vector<Double_t>   activity;
	      vector<Double_t>   pActivity;


	ClassDef(TNuclide,1);

};

#endif

