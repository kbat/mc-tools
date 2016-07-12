Table *T = new Table();

void loadTable() {

	TFile *f = new TFile("alltabs.root"); // Change to the correct file name in case different from the default one
	TTree *alltabs = (TTree *) f->Get("alltabs");

	TBranch *bT = alltabs->GetBranch("Table");
	bT->SetAddress(&T);
	bT->GetEntry(0);

	cout << "Number of nuclides in table: " << T->getNNuclides() << endl;
	cout << "Number of time steps in table: " << T->getNBeamStates() << endl;

}

