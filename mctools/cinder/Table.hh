#ifndef TABLE_HH
#define TABLE_HH

#include "Globals.hh"
#include "Nuclide.hh"

class Table {

	public:

		Table(string,int);
		~Table() {};

		void addBeamState(bool);
		void addTimeStep(double);

		void printTimeSteps();

		bool getBeamState(int i) { return beamStates.at(i); };
		vector<double> getTimeSteps() {};
		vector<double> getCumulativeTimeSteps() {};

		string getTableName() { return tableName; };
		int getTableNumber() { return tableNumber; };

		int addNuclide(Nuclide);
		Nuclide* editNuclide(int);
		int findNuclide(string n);

		int getTotalNuclides() { return Nuclides.size(); };
		int getTotalBeamStates() { return beamStates.size(); };

		void finalizeTable();

	private:

		string tableName;
		int tableNumber;

		vector<bool> beamStates;
		vector<double> timeSteps;

		vector<Nuclide> Nuclides;

};

Table::Table(string name, int number) {

	tableName = name;
	tableNumber = number;

}

void Table::addBeamState(bool s) {

	beamStates.push_back(s);

}

void Table::addTimeStep(double tS) {

	timeSteps.push_back(tS);

}

int Table::addNuclide(Nuclide n) {

	Nuclides.push_back(n);

	//cout.precision(5);
	//cout << "Adding nuclide: " << n.getName() << " with halflife: " << n.getHalflife() << std::scientific << endl;

	return (Nuclides.size()-1);

}

void Table::printTimeSteps() {

	for (int i=0; i < beamStates.size(); i++) {

		//cout << "Bs: " << beamStates.at(i) << " - Ts: " << timeSteps.at(i) << endl;
		cout << beamStates.at(i) << " ";

	}

	cout << endl;

}

Nuclide* Table::editNuclide(int i) {

	return &Nuclides.at(i);

}

int Table::findNuclide(string n) {

	int pos = -1;

	for (int i = 0; i < Nuclides.size(); i++) {

		if (Nuclides.at(i).getName() == n) {

			pos = i;
			break;

		}

	}

	return pos;

}

void Table::finalizeTable() {

	int max = getTotalBeamStates();

	for (int i=0; i < getTotalNuclides(); i++) {

		editNuclide(i)->trimActivities(max);
		editNuclide(i)->applySign(beamStates);

	}

}

#endif

