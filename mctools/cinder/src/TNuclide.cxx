#include "TNuclide.h"

#ifndef __CLING__
        ClassImp(TNuclide)
#endif

TNuclide::TNuclide(string name, Double_t hL) {

        fNuclideName = name;
        SetExcited();

        fHalfLife = hL;

}

void TNuclide::SetName(string name) {

        fNuclideName = name;
        SetExcited();

}

void TNuclide::SetHalflife(Double_t hL) {

        fHalfLife = hL;

}

Double_t TNuclide::GetHalflife() const {

        return fHalfLife;

}

void TNuclide::SetExcited() {

        if (fNuclideName.find("*") != std::string::npos) {

                fIsExcited = true;

        } else {

                fIsExcited = false;

        }

}

const char *TNuclide::GetName() const {

        return fNuclideName.c_str();

}

ULong_t TNuclide::GetNActivity() const {

        return fActivity.size();

}

void TNuclide::AddActivity(Double_t act) {

        fActivity.push_back(act);

}

void TNuclide::TrimActivity(Int_t max) {

        for (Int_t i = (fActivity.size() - 1); i >= max; i--) {

                fActivity.erase(fActivity.begin() + i);

        }

}

Bool_t TNuclide::GetExcited() const {

        return fIsExcited;

}

vector<Double_t> TNuclide::GetActivities() const {

        return fActivity;

}

Double_t TNuclide::GetActivity(Int_t i) const {

        return fActivity.at(i);

}

Double_t TNuclide::GetPActivity(Int_t i) const {

        return fPActivity.at(i);

}

void TNuclide::CalculatePercent(vector<Double_t> totals) {

        if (totals.size() == fActivity.size()) {

                for (UInt_t i=0; i < fActivity.size(); i++) {

                        fPActivity.push_back(fActivity.at(i)/totals.at(i)*100.);

                }

        } else {

                cout << "This method cannot be accessed directly" << endl;

        }

}







