#include "TTable.h"
#include "TNuclide.h"

#include <TROOT.h>
#include <TEnv.h>
#include <TVector.h>
#include <TGraph.h>
#include <TMultiGraph.h>
#include <TApplication.h>
#include <TFile.h>
#include <TTree.h>
#include <TSystem.h>
#include <TH1F.h>
#include <TCanvas.h>
#include <TStyle.h>
#include <TObject.h>

#include <Riostream.h>

#include <fstream>
#include <iostream>
#include <iomanip>
#include <sstream>
#include <string>
#include <cstdlib>
#include <vector>

using namespace std;

////////// ERROR CODES ///////////////////////////

// Exit status 0 --> Success
// Exit status 1 --> Alltabs file not found
// Exit status 2 --> Too few arguments

//////////////////////////////////////////////////

////////// FUNCTION DECLARATIONS /////////////////

void   HelpLine(TApplication *);
void   Read(ifstream &, TBranch *, TTable *, TNuclide *);
void   readTimeAndBeamHeadings(ifstream &, string, TTable *);

//////////////////////////////////////////////////

Int_t main(Int_t argc, char* argv[]) {

        TApplication *rootApp = new TApplication("alltabs2ttree",&argc,argv);

                ifstream   alltabs;

            stringstream   rootFile;

                  TTable  *table;
                TNuclide  *nuclide;

                   TTree  *T;

                 TBranch  *bTable;

        if (rootApp->Argc() == 1) {

                HelpLine(rootApp);
                return 2;

        } else {

                gSystem->Load("libTree");
                gSystem->Load("libAlltabs");

                table = new TTable();
                nuclide = new TNuclide();

                T = new TTree("alltabs","TABLE 4",0);
                bTable = T->Branch("Table", &table, 0);
                
                alltabs.open(rootApp->Argv(1));

                if (alltabs.is_open()) {

                        Read(alltabs, bTable, table, nuclide);

                        if (rootApp->Argc() == 2) {

                                rootFile << rootApp->Argv(1) << ".root";

                        } else {

                                rootFile << rootApp->Argv(2);

                        }

                        T->SaveAs((rootFile.str()).c_str());

                        return 0;

                } else {

                        cerr << "The requested alltabs file either does not exist or is corrupted." << endl;
                        return 1;

                 }

        }

}

void HelpLine(TApplication *rA) {

        cout << "Error: too few arguments." << endl;
        cout << "Usage: " << rA->Argv(0) << " alltabs [output filename]" << endl;

}

void Read(ifstream &alltabs, TBranch *bTable, TTable *table, TNuclide *nuclide) {

        ////////// DECLARATIONS //////////////////////////

                  Bool_t   inTable = false;
                  Bool_t   timeStepsDone = false;

                   Int_t   tNumber;
                   Int_t   existingNuclide;
                Double_t   hL;

                  string   pline;
                  string   line;
                  string   dummy;
                  string   element;
                  string   isotope;

            stringstream   ssline;
        vector<Double_t>   activities(10);

        //////////////////////////////////////////////////

        pline = "";

        while (getline(alltabs,line)) {

                if (line.find("TOTAL ACTIVITY (CURIES) BY NUCLIDE IN") != std::string::npos ) {

                        ssline << pline;
                        ssline >> tNumber >> dummy >> tNumber;

                        table->SetName(line);
                        table->SetNumber(tNumber);

                        inTable = true;

                        ssline.str(string());
                        ssline.clear();

                }

                if ( (inTable) && (!timeStepsDone) && ((line.find("UP") != std::string::npos) || (line.find("DOWN") != std::string::npos)) ) {

                        readTimeAndBeamHeadings(alltabs,line,table);

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

                                existingNuclide = table->FindNuclide(element+isotope);

                                if (existingNuclide == -1) {

                                        nuclide = new TNuclide(element+isotope,hL);
                                        existingNuclide = table->AddNuclide(*nuclide);

                                }

                                nuclide = table->GetNuclide(existingNuclide);

                                for (Int_t i = 0; i < 10; i++) {

                                        nuclide->AddActivity(activities.at(i));

                                }

                                ssline.str(string());
                                ssline.clear();

                                element = isotope = "";

                        }

                }

        }

        table->FinalizeTable();

        bTable->Fill();

        alltabs.close();

}

void readTimeAndBeamHeadings(ifstream &alltabs, string line, TTable *table) {

        ////////// DECLARATIONS //////////////////////////

                  Bool_t   bS;

          vector<string>   beamStates(10);
          vector<string>   timeStepsUnit(10);
        vector<Double_t>   timeSteps(10);

            stringstream   ssline;
                  string   dummy;

        //////////////////////////////////////////////////

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

        for (Int_t i = 0; i < 10 ; i++) {

                if (timeStepsUnit.at(i) == "H") {

                        timeSteps.at(i) *= 3600.;

                }

                if (timeStepsUnit.at(i) == "D") {

                        timeSteps.at(i) *= 86400.;

                }

                if (timeStepsUnit.at(i) == "Y") {

                        timeSteps.at(i) *= 31536000.;

                }

                if (beamStates.at(i) == "UP") {

                        bS = true;

                } else {

                        bS = false;

                }

                if ( (beamStates.at(i) != "") && (timeSteps.at(i) != 0) ) {

                        table->AddBeamState(bS);
                        table->AddTimeStep(timeSteps.at(i));

                }

                beamStates.at(i) = string();
                timeSteps.at(i)  = 0;

        }

        ssline.str(string());
        ssline.clear();

}
