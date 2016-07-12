// This function must be called from within ROOT with the following syntax:
// .x loadTable.C("alltabs.root")
// Change the filename according to your needs

Table *T = new Table();

void loadTable(string name) {

	TFile *f = new TFile(name.c_str());
	TTree *alltabs = (TTree *) f->Get("alltabs");

	TBranch *bT = alltabs->GetBranch("Table");
	bT->SetAddress(&T);
	bT->GetEntry(0);

	cout << "Number of nuclides in table: " << T->getNNuclides() << endl;
	cout << "Number of time steps in table: " << T->getNBeamStates() << endl;

}

