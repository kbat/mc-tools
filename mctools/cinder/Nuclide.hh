#ifndef NUCLIDE_HH
#define NUCLIDE_HH

#include "Globals.hh"

class Nuclide {

	public:

				 Nuclide(string,double);
				~Nuclide() {};

			  void   addActivity(double);

			string   getName() { return nuclideName; }
			double   getHalflife() {return halfLife; }
			double   getActivity(int i) { return activity.at(i); }

			  void   printInfo();

			   int   getActivityNumber() { return activity.size(); }

			  void   trimActivities(int);
			  void   applySign(vector<bool>);

	private:

			string   nuclideName;
			double   halfLife;

			  bool   isExcited;

		vector<double>   activity;

};

Nuclide::Nuclide(string name, double hL) {

	nuclideName = name;
	halfLife = hL;

	if (nuclideName.find("*") != std::string::npos) {

		isExcited = true;

	} else {

		isExcited = false;

	}

}

void Nuclide::addActivity(double act) {

	activity.push_back(act);

}

void Nuclide::printInfo() {

	cout.precision(5);
	cout << nuclideName << " " << halfLife << scientific << " ";

	for (int i = 0; i < activity.size(); i++) {

		cout << activity.at(i) << scientific << " ";

	}

	cout << endl;

}

void Nuclide::trimActivities(int max) {

	for (int i = (activity.size() - 1); i >= max; i--) {

		activity.erase(activity.begin() + i);

	}

}

void Nuclide::applySign(vector <bool> bState) {

	for (int i = 0; i < bState.size(); i++) {

		if (!(bState.at(i))) {

			activity.at(i) *= -1.0;

		}

	}

}

#endif

