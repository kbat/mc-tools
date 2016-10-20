#include "Nuclide.hh"

#ifndef __CINT__
	ClassImp(Nuclide)
#endif

Nuclide::Nuclide(string name, Double_t hL) {

	nuclideName = name;
	setExcited();

	halfLife = hL;

}

void Nuclide::setName(string name) {

	nuclideName = name;
	setExcited();

}

void Nuclide::setHalflife(Double_t hL) {

	halfLife = hL;

}

Double_t Nuclide::getHalflife() {

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

Int_t Nuclide::getNActivity() {

	return activity.size();

}

void Nuclide::addActivity(Double_t act) {

	activity.push_back(act);

}

void Nuclide::trimActivity(Int_t max) {

	for (Int_t i = (activity.size() - 1); i >= max; i--) {

		activity.erase(activity.begin() + i);

	}

}

Bool_t Nuclide::getExcited() {

	return isExcited;

}

vector<Double_t> Nuclide::getActivities() {

	return activity;

}

Double_t Nuclide::getActivity(Int_t i) {

	return activity.at(i);

}

Double_t Nuclide::getPActivity(Int_t i) {

	return pActivity.at(i);

}

void Nuclide::calculatePercent(vector<Double_t> totals) {

	if (totals.size() == activity.size()) {

		for (UInt_t i=0; i < activity.size(); i++) {

			pActivity.push_back(activity.at(i)/totals.at(i)*100.);

		}

	} else {

		cout << "This method cannot be accessed directly" << endl;

	}

}







