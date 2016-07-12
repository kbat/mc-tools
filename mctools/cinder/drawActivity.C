Table *T = new Table();

void drawActivity() {

	string nuclideName = "W183*"; // Change to the exact name of the desired isotope

	TFile *f = new TFile("alltabs.root"); // Change to the correct file name in case different from the default one
	TTree *alltabs = (TTree *) f->Get("alltabs");

	TBranch *bT = alltabs->GetBranch("Table");
	bT->SetAddress(&T);
	bT->GetEntry(0);

	cout << "Number of nuclides in table: " << T->getNNuclides() << endl;
	cout << "Number of time steps in table: " << T->getNBeamStates() << endl;

	int nS = T->getNBeamStates();

	double *X;
	X = (double *) malloc(nS*sizeof(double));

	for (int i=0; i < nS; i++) {

		X[i] = i;

	}

	double *A = &((T->getNuclide(T->findNuclide(nuclideName)))->getActivities())[0];

	TGraph *g = new TGraph(nS,X,A);

	g->Draw("AC*");

}

