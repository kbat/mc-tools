#include "TNuclide.h"

#ifndef __CINT__
        ClassImp(TNuclide)
#endif

TNuclide::TNuclide(string name, Double_t hL) {

        nuclideName = name;
        setExcited();

        halfLife = hL;

}

void TNuclide::setName(string name) {

        nuclideName = name;
        setExcited();

}

void TNuclide::setHalflife(Double_t hL) {

        halfLife = hL;

}

Double_t TNuclide::getHalflife() const {

        return halfLife;

}

void TNuclide::setExcited() {

        if (nuclideName.find("*") != std::string::npos) {

                isExcited = true;

        } else {

                isExcited = false;

        }

}

string TNuclide::getName() const {

        return nuclideName;

}

ULong_t TNuclide::getNActivity() const {

        return activity.size();

}

void TNuclide::addActivity(Double_t act) {

        activity.push_back(act);

}

void TNuclide::trimActivity(Int_t max) {

        for (Int_t i = (activity.size() - 1); i >= max; i--) {

                activity.erase(activity.begin() + i);

        }

}

Bool_t TNuclide::getExcited() const {

        return isExcited;

}

vector<Double_t> TNuclide::getActivities() const {

        return activity;

}

Double_t TNuclide::getActivity(Int_t i) const {

        return activity.at(i);

}

Double_t TNuclide::getPActivity(Int_t i) const {

        return pActivity.at(i);

}

void TNuclide::calculatePercent(vector<Double_t> totals) {

        if (totals.size() == activity.size()) {

                for (UInt_t i=0; i < activity.size(); i++) {

                        pActivity.push_back(activity.at(i)/totals.at(i)*100.);

                }

        } else {

                cout << "This method cannot be accessed directly" << endl;

        }

}







