#include "Nuclide.hh"

#ifndef __CINT__
	ClassImp(Nuclide)
#endif

Nuclide::Nuclide(string name, double hL) {

	nuclideName = name;
	setExcited();

	halfLife = hL;

}

void Nuclide::setName(string name) {

	nuclideName = name;
	setExcited();

}

void Nuclide::setHalflife(double hL) {

	halfLife = hL;

}

double Nuclide::getHalflife() {

	return halfLife;

}

void Nuclide::setExcited() {

	if (nuclideName.find("*") != std::string::npos) {

		isExcited = true;

	} else {

		isExcited = false;

	}

}

string Nuclide::getName() {

	return nuclideName;

}

int Nuclide::getNActivity() {

	return activity.size();

}

void Nuclide::addActivity(double act) {

	activity.push_back(act);

}

void Nuclide::trimActivity(int max) {

	for (int i = (activity.size() - 1); i >= max; i--) {

		activity.erase(activity.begin() + i);

	}

}

bool Nuclide::getExcited() {

	return isExcited;

}

vector<double> Nuclide::getActivities() {

	return activity;

}

double Nuclide::getActivity(int i) {

	return activity.at(i);

}

double Nuclide::getPActivity(int i) {

	return pActivity.at(i);

}

void Nuclide::calculatePercent(vector<double> totals) {

	if (totals.size() == activity.size()) {

		for (UInt_t i=0; i < activity.size(); i++) {

			pActivity.push_back(activity.at(i)/totals.at(i)*100.);

		}

	} else {

		cout << "This method cannot be accessed directly" << endl;

	}

}







