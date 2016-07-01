#include "Table.hh"

////////// DECLARATIONS //////////////////////////

      ifstream   alltabs;
	
	  bool   inTable = false;
	  bool   timeStepsDone = false;
	  bool   bS;
	   int   tNumber;
	   int   existingNuclide;
	double   hL;

	string   pline;
	string   line;
	string   dummy;
	string   element;
	string   isotope;

  stringstream   ssline;

vector<string>   beamStates(10);
vector<string>   timeStepsUnit(10);
vector<double>   timeSteps(10);
vector<double>   activities(10);

	 Table  *table;
       Nuclide  *nuclide;

//////////////////////////////////////////////////

	  void   readTimeAndBeamHeadings();

//////////////////////////////////////////////////

int main() {

	alltabs.open("alltabs");

	pline = "";

	while (getline(alltabs,line)) {

		if (line.find("TOTAL ACTIVITY (CURIES) BY NUCLIDE IN") != std::string::npos ) {

			ssline << pline;
			ssline >> tNumber >> dummy >> tNumber;

			table = new Table(line,tNumber);

			inTable = true;

			ssline.str(string());
			ssline.clear();

		}

		if ( (inTable) && (!timeStepsDone) && ((line.find("UP") != std::string::npos) || (line.find("DOWN") != std::string::npos)) ) {

			readTimeAndBeamHeadings();

			timeStepsDone = true;

		}

		if ( (inTable) && (line.find("(CONTINUED AT SUBSEQUENT TIMES)") != std::string::npos) ) {

			timeStepsDone = false;

		} else if ( (inTable) && (line.find("TABLE") != std::string::npos) && (line.find("(CONTINUED AT SUBSEQUENT TIMES)") == std::string::npos) ) {

			continue;

		}

		if ( (inTable) && (line.find("DECAY POWER DENSITY (WATTS/CC) BY NUCLIDE IN") != std::string::npos) ) {

			inTable = false;
			timeStepsDone = false;

			break;

		}

		if (line.find("TABLE") != std::string::npos) {

			pline = line;

		}

		if ( (inTable) && (timeStepsDone) ) {

			if ( (line.find("UP") != std::string::npos) ||
			     (line.find("DOWN") != std::string::npos) ||
			     (line.find("NUCLIDE") != std::string::npos) ||
			     (line.find("+_______") != std::string::npos) ||
			     (line.find("  A<66") != std::string::npos) ||
			     (line.find(" 65<A<173") != std::string::npos) ||
			     (line.find(" 172<A") != std::string::npos) ||
			     (line.find(" TOTAL") != std::string::npos) ) {

				continue;

			}
	
			ssline << line.substr(0,9);
			ssline >> element >> isotope;

			if ((element+isotope) != "" ) {

				ssline.str(string());
				ssline.clear();

				ssline << line.substr(10,string::npos);
				ssline >> hL >> activities.at(0) >> activities.at(1)
					     >> activities.at(2)
					     >> activities.at(3)
					     >> activities.at(4)
					     >> activities.at(5)
					     >> activities.at(6)
					     >> activities.at(7)
					     >> activities.at(8)
					     >> activities.at(9);

				existingNuclide = table->findNuclide(element+isotope);

				if (existingNuclide == -1) {

					nuclide = new Nuclide(element+isotope,hL);
					existingNuclide = table->addNuclide(*nuclide);

				}

				nuclide = table->editNuclide(existingNuclide);

				for (int i = 0; i < 10; i++) {

					nuclide->addActivity(activities.at(i));

				}

				ssline.str(string());
				ssline.clear();

				element = isotope = "";

			}

		}

	}

	table->finalizeTable();

	table->printTimeSteps();

	for (int i = 0; i < table->getTotalNuclides(); i++) {

		(table->editNuclide(i))->printInfo();

	}

	alltabs.close();

	return 0;

}

void readTimeAndBeamHeadings() {

	ssline << line;
	ssline >> beamStates.at(0)
	       >> beamStates.at(1)
	       >> beamStates.at(2)
	       >> beamStates.at(3)
	       >> beamStates.at(4)
	       >> beamStates.at(5)
	       >> beamStates.at(6)
	       >> beamStates.at(7)
	       >> beamStates.at(8)
	       >> beamStates.at(9);
	      

	getline(alltabs,line);

	ssline.str(string());
	ssline.clear();

	ssline << line;
	ssline >> dummy >> dummy >> timeSteps.at(0) >> timeStepsUnit.at(0)
				 >> timeSteps.at(1) >> timeStepsUnit.at(1)
				 >> timeSteps.at(2) >> timeStepsUnit.at(2)
				 >> timeSteps.at(3) >> timeStepsUnit.at(3)
				 >> timeSteps.at(4) >> timeStepsUnit.at(4)
				 >> timeSteps.at(5) >> timeStepsUnit.at(5)
				 >> timeSteps.at(6) >> timeStepsUnit.at(6)
				 >> timeSteps.at(7) >> timeStepsUnit.at(7)
				 >> timeSteps.at(8) >> timeStepsUnit.at(8)
				 >> timeSteps.at(9) >> timeStepsUnit.at(9);

	for (int i = 0; i < 10 ; i++) {

		if (timeStepsUnit.at(i) == "D") {

			timeSteps.at(i) *= 86400.;

		}

		if (beamStates.at(i) == "UP") {

			bS = true;

		} else {

			bS = false;

		}

		if ( (beamStates.at(i) != "") && (timeSteps.at(i) != 0) ) {

			table->addBeamState(bS);
			table->addTimeStep(timeSteps.at(i));

		}

		beamStates.at(i) = string();
		timeSteps.at(i)  = 0;

	}

	ssline.str(string());
	ssline.clear();

};

