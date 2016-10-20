#include "Table.hh"

#ifndef __CINT__
	ClassImp(Table)
#endif

Table::Table(string name, Int_t number) {

	tableName = name;
	tableNumber = number;

}

void Table::setName(string name) {

	tableName = name;

}

void Table::setNumber(Int_t number) {

	tableNumber = number;

}

string Table::getName() {

	return tableName;

}

Int_t Table::getNumber() {

	return tableNumber;

}

ULong_t Table::getNNuclides() {

	return Nuclides.size();

}

ULong_t Table::getNBeamStates() {

	return beamStates.size();

}

void Table::addBeamState(Bool_t s) {

	beamStates.push_back(s);

}

void Table::addTimeStep(Double_t tS) {

	timeSteps.push_back(tS);

}

ULong_t Table::addNuclide(Nuclide n) {

	Nuclides.push_back(n);

	return (Nuclides.size()-1);

}

Nuclide* Table::getNuclide(Int_t i) {

	return &Nuclides.at(i);

}

Int_t Table::findNuclide(string n) {

	Int_t pos = -1;

	for (UInt_t i = 0; i < Nuclides.size(); i++) {

		if (Nuclides.at(i).getName() == n) {

			pos = i;
			break;

		}

	}

	return pos;

}

void Table::finalizeTable() {

	Int_t max = getNBeamStates();

	for (ULong_t i=0; i < getNNuclides(); i++) {

		getNuclide(i)->trimActivity(max);

	}

}

vector<Double_t> Table::getTimeSteps() {

	return timeSteps;

}

vector<Bool_t> Table::getBeamStates() {

	return beamStates;

}

void Table::listNuclides() {

	for (UInt_t i=0; i < Nuclides.size(); i++) {

		cout << i << ": " << (Nuclides.at(i)).getName() << endl;
	}

}

void Table::listNuclides(string n) {

	string nuclideName;

	for (UInt_t i=0; i < Nuclides.size(); i++) {

		nuclideName = (Nuclides.at(i)).getName();

		if (nuclideName.find(n) != std::string::npos) {

			cout << i << ": " << nuclideName << endl;

		}

	}

}

void Table::calculateTotals() {

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

void Table::toPercent() {

	for (ULong_t i=0; i < getNNuclides(); i++) {

		getNuclide(i)->calculatePercent(totalActivity);

	}

}

void Table::getMostActive(Double_t threshold, Int_t timeStep) {

	Int_t min = 0;
	Int_t max = getNBeamStates();

	Nuclide *N;

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

vector<Double_t> Table::getTotalActivity() {

	if (totalActivity.size() != getNBeamStates()) {

		calculateTotals();

	} 

	return totalActivity;

}




