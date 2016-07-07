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

			  void   calculatePercentActivity(vector<double>);

	private:

			string   nuclideName;
			double   halfLife;

			  bool   isExcited;

		vector<double>   activity;
		vector<double>   percentActivity;

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

	for (int i = 0; i < percentActivity.size(); i++) {

		cout << percentActivity.at(i) << scientific << " ";

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

void Nuclide::calculatePercentActivity(vector<double> totals) {

	double tmpPAct;

	for (int i = 0; i < activity.size(); i++) {

		tmpPAct = activity.at(i) / totals.at(i);

		percentActivity.push_back(tmpPAct);

	}

}

#endif

