#include "TTable.h"

#ifndef __CINT__
	ClassImp(TTable)
#endif

TTable::TTable(string name, Int_t number) {

	tableName = name;
	tableNumber = number;

}

void TTable::setName(string name) {

	tableName = name;

}

void TTable::setNumber(Int_t number) {

	tableNumber = number;

}

string TTable::getName() {

	return tableName;

}

Int_t TTable::getNumber() {

	return tableNumber;

}

ULong_t TTable::getNNuclides() {

	return Nuclides.size();

}

ULong_t TTable::getNBeamStates() {

	return beamStates.size();

}

void TTable::addBeamState(Bool_t s) {

	beamStates.push_back(s);

}

void TTable::addTimeStep(Double_t tS) {

	timeSteps.push_back(tS);

}

ULong_t TTable::addNuclide(TNuclide n) {

	Nuclides.push_back(n);

	return (Nuclides.size()-1);

}

TNuclide* TTable::getNuclide(Int_t i) {

	return &Nuclides.at(i);

}

Int_t TTable::findNuclide(string n) {

	Int_t pos = -1;

	for (UInt_t i = 0; i < Nuclides.size(); i++) {

		if (Nuclides.at(i).getName() == n) {

			pos = i;
			break;

		}

	}

	return pos;

}

void TTable::finalizeTable() {

	Int_t max = getNBeamStates();

	for (ULong_t i=0; i < getNNuclides(); i++) {

		getNuclide(i)->trimActivity(max);

	}

}

vector<Double_t> TTable::getTimeSteps() {

	return timeSteps;

}

vector<Bool_t> TTable::getBeamStates() {

	return beamStates;

}

void TTable::listNuclides() {

	for (UInt_t i=0; i < Nuclides.size(); i++) {

		cout << i << ": " << (Nuclides.at(i)).getName() << endl;
	}

}

void TTable::listNuclides(string n) {

	string nuclideName;

	for (UInt_t i=0; i < Nuclides.size(); i++) {

		nuclideName = (Nuclides.at(i)).getName();

		if (nuclideName.find(n) != std::string::npos) {

			cout << i << ": " << nuclideName << endl;

		}

	}

}

void TTable::calculateTotals() {

	Double_t tmp;

	for (ULong_t i=0; i < getNNuclides(); i++) {

		for (ULong_t j=0; j < getNBeamStates(); j++) {

			tmp = (Nuclides.at(i)).getActivity(j);

			if (i == 0) {

				totalActivity.push_back(tmp);

			} else {

				totalActivity.at(j) += tmp;

			}

		}

	}

}

void TTable::toPercent() {

	for (ULong_t i=0; i < getNNuclides(); i++) {

		getNuclide(i)->calculatePercent(totalActivity);

	}

}

void TTable::getMostActive(Double_t threshold, Int_t timeStep) {

	Int_t min = 0;
	Int_t max = getNBeamStates();

	TNuclide *N;

	Double_t Activity;
	Double_t pActivity;

	if ( (timeStep != -1) && (0 <= timeStep) && (timeStep <= static_cast<Int_t>(getNBeamStates()-1)) ) {

		min = timeStep;
		max = timeStep+1;

	}

	if (totalActivity.size() != getNBeamStates()) {

		calculateTotals();
		toPercent();

	}

	for (ULong_t i = 0; i < getNNuclides(); i++) {

		N = getNuclide(i);

		for (Int_t j = min; j < max; j++) {

			pActivity = N->getPActivity(j);
			Activity = N->getActivity(j);

			if (pActivity >= threshold) {

				cout << j << ": " << N->getName() << " (" << pActivity << ") " << Activity*3.7E10 << " Bq" << endl;

			}

		}

	}

}

vector<Double_t> TTable::getTotalActivity() {

	if (totalActivity.size() != getNBeamStates()) {

		calculateTotals();

	} 

	return totalActivity;

}




