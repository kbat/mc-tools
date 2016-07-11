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

vector<double> Nuclide::getActivity() {

	return activity;

}




