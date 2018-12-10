#include "TTable.h"

#ifndef __CLING__
        ClassImp(TTable)
#endif

TTable::TTable(string name, Int_t number) {

        fTableName = name;
        fTableNumber = number;

}

void TTable::SetName(string name) {

        fTableName = name;

}

void TTable::SetNumber(Int_t number) {

        fTableNumber = number;

}

const char *TTable::GetName() const {

        return fTableName.c_str();

}

Int_t TTable::GetNumber() const {

        return fTableNumber;

}

ULong_t TTable::GetNNuclides() const {

        return fNuclides.size();

}

ULong_t TTable::GetNBeamStates() const {

        return fBeamStates.size();

}

void TTable::AddBeamState(Bool_t s) {

        fBeamStates.push_back(s);

}

void TTable::AddTimeStep(Double_t tS) {

        fTimeSteps.push_back(tS);

}

ULong_t TTable::AddNuclide(TNuclide n) {

        fNuclides.push_back(n);

        return (fNuclides.size()-1);

}

TNuclide* TTable::GetNuclide(Int_t i) {

        return &fNuclides.at(i);

}

Int_t TTable::FindNuclide(string n) {

        Int_t pos = -1;
        for (UInt_t i = 0; i < fNuclides.size(); i++) {

                if (string(fNuclides.at(i).GetName()) == n) {

                        pos = i;
                        break;

                }

        }

        return pos;

}

void TTable::FinalizeTable() {

        Int_t max = GetNBeamStates();

        for (ULong_t i=0; i < GetNNuclides(); i++) {

                GetNuclide(i)->TrimActivity(max);

        }

}

vector<Double_t> TTable::GetTimeSteps() const {

        return fTimeSteps;

}

vector<Bool_t> TTable::GetBeamStates() const {

        return fBeamStates;

}

void TTable::ListNuclides() {

        for (UInt_t i=0; i < fNuclides.size(); i++) {

                cout << i << ": " << (fNuclides.at(i)).GetName() << endl;
        }

}

void TTable::ListNuclides(string n) {

        string nuclideName;

        for (UInt_t i=0; i < fNuclides.size(); i++) {

                nuclideName = string((fNuclides.at(i)).GetName());

                if (nuclideName.find(n) != std::string::npos) {

                        cout << i << ": " << nuclideName << endl;

                }

        }

}

void TTable::CalculateTotals() {

        Double_t tmp;

        for (ULong_t i=0; i < GetNNuclides(); i++) {

                for (ULong_t j=0; j < GetNBeamStates(); j++) {

                        tmp = (fNuclides.at(i)).GetActivity(j);

                        if (i == 0) {

                                fTotalActivity.push_back(tmp);

                        } else {

                                fTotalActivity.at(j) += tmp;

                        }

                }

        }

}

void TTable::ToPercent() {

        for (ULong_t i=0; i < GetNNuclides(); i++) {

                GetNuclide(i)->CalculatePercent(fTotalActivity);

        }

}

void TTable::GetMostActive(Double_t threshold, Int_t timeStep) {

        Int_t min = 0;
        Int_t max = GetNBeamStates();

        TNuclide *N;

        Double_t Activity;
        Double_t pActivity;

        if ( (timeStep != -1) && (0 <= timeStep) && (timeStep <= static_cast<Int_t>(GetNBeamStates()-1)) ) {

                min = timeStep;
                max = timeStep+1;

        }

        if (fTotalActivity.size() != GetNBeamStates()) {

                CalculateTotals();
                ToPercent();

        }

        for (ULong_t i = 0; i < GetNNuclides(); i++) {

                N = GetNuclide(i);

                for (Int_t j = min; j < max; j++) {

                        pActivity = N->GetPActivity(j);
                        Activity = N->GetActivity(j);

                        if (pActivity >= threshold) {

                                cout << j << ": " << N->GetName() << " (" << pActivity << ") " << Activity*3.7E10 << " Bq" << endl;

                        }

                }

        }

}

vector<Double_t> TTable::GetTotalActivity() {

        if (fTotalActivity.size() != GetNBeamStates()) {

                CalculateTotals();

        } 

        return fTotalActivity;

}




