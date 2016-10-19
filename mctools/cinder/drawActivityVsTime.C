Table *T = new Table();

Int_t drawActivityVsTime(string name) {

	TFile *f = new TFile(name.c_str());
	TTree *alltabs = (TTree *) f->Get("alltabs");

	TBranch *bT = alltabs->GetBranch("Table");
	bT->SetAddress(&T);
	bT->GetEntry(0);

	cout << "Number of nuclides in table: " << T->getNNuclides() << endl;
	cout << "Number of time steps in table: " << T->getNBeamStates() << endl;

	ULong_t nS = T->getNBeamStates();

	vector<Double_t> timeSteps = T->getTimeSteps();

	Double_t *X;
	X = (Double_t *) malloc(nS*sizeof(Double_t));

	X[0] = 0.;
	//X[0] = timeSteps.at(0); // Uncomment to include also the first step

	for (ULong_t i = 1; i < nS; i++) {

		X[i] = X[i-1] + (timeSteps.at(i));

	}

	Double_t *A = &(T->getTotalActivity())[0];

	//TGraph *g = new TGraph(nS); // Uncomment to include also the first step
	TGraph *g = new TGraph((Int_t)nS-1); // Comment if the above is uncommented

	/* for (ULong_t i = 0;  i < nS; i++) { // Uncomment to include also the first step

		g->SetPoint(i,X[i]/86400,(T->getTotalActivity())[i]*3.7E10/12.7/7.85);
		cout << g->GetX()[i] << "   " << g->GetY()[i] << endl;

	}*/

	for (ULong_t i = 1; i < nS; i++) { // Comment if the above is uncommented

		g->SetPoint((Int_t)i-1,X[i]/86400,(T->getTotalActivity())[i]*3.7E10/12.7/19.3);
		cout << g->GetX()[i-1] << "   " << g->GetY()[i-1] << endl;

	}

	g->Draw("AL*");
	g->GetXaxis()->SetMoreLogLabels();
	g->SetName(name.c_str());

	gPad->SetLogx();
	gPad->SetLogy();

	TFile *f = new TFile("SteelDecays.root","UPDATE");
	g->Write();
	f->Close();

	return 0;

}
