#include "alltabs.hh"

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <array>
#include <vector>

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

#include <Riostream.h>

using namespace std;

int main(int argc, char* argv[]) {

	TApplication *rootApp = new TApplication("alltabs2ttree",&argc,argv);

	gSystem->Load("libTree");

	Table *t = Read();

	cout << t->getTableName() << endl;

	return 0;

}
