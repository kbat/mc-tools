Table *T = new Table();
TH2D *act;

drawActivity3D(string name, char *mode = "p", int binLow = -1, int binUp = -1) {

	TFile *f = new TFile(name.c_str());
	TTree *alltabs = (TTree *) f->Get("alltabs");

	TBranch *bT = alltabs->GetBranch("Table");
	bT->SetAddress(&T);
	bT->GetEntry(0);

	cout << "Number of nuclides in table: " << T->getNNuclides() << endl;
	cout << "Number of time steps in table: " << T->getNBeamStates() << endl;

	int nS = T->getNBeamStates();
	int nN, binOffset;

	if ( (binLow == -1) && (binUp == -1) ) {

		nN = T->getNNuclides();
		binOffset = 0;

	} else {

		nN = (binUp - binLow) + 1;
		binOffset = binLow;

	}

	double *X,*Y;
	X = (double *) malloc((nS+1)*sizeof(double));
	Y = (double *) malloc((nN+1)*sizeof(double));

	for (int i=0; i <= nS; i++) {

		X[i] = i;

	}

	for (int i=0; i <= nN; i++) {

		Y[i] = i;

	}
	
	act = new TH2D("drivingNuclide","Driving nuclides (TABLE 4)",nN,Y,nS,X);
	act->SetXTitle("Nuclide number (n+1)");
	act->SetYTitle("Timestep (t+1)");

	double A;

	T->getMostActive(100,0);
	vector<double> timeSteps = T->getTimeSteps();
	stringstream tSS;

	for (int i = 1; i <= nN; i++) {

		for (int j = 1; j <= nS; j++) {

			if (mode == "p") { // get PERCENT activity

				cout << "PERCENT mode" << endl;
				A = (T->getNuclide((i-1)+binOffset))->getPActivity(j-1);

			} else if (mode == "a") { // get ABSOLUTE activity

				cout << "ABSOLUTE mode" << endl;
				A = (T->getNuclide((i-1)+binOffset))->getActivity(j-1);

			}
			act->SetBinContent(i,j,A);
			act->GetXaxis()->SetBinLabel(i,(T->getNuclide((i-1)+binOffset)->getName()).c_str());
			tSS << timeSteps.at(j-1);
			act->GetYaxis()->SetBinLabel(j,(tSS.str()).c_str());

			tSS.str(string());
			tSS.clear();

		}

	}

	gStyle->SetOptStat(0);
	act->GetXaxis()->SetRange(binLow,binUp);
	if (mode == "p") {

		act->GetZaxis()->SetRangeUser(1E-2,1E2);

	}
	act->Draw("colz");
	gPad->SetLogz();

	T->listNuclides();

	return 0;

}
