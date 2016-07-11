drawActivity() {

        string nuclideName = "W183*";

        TFile *f = new TFile("alltabs-024.root");
        TTree *alltabs = (TTree *) f->Get("alltabs");

        Table *T = new Table();

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

        double *A = &((T->getNuclide(T->findNuclide(nuclideName)))->getActivity())[0];

        TGraph *g = new TGraph(nS,X,A);

        g->Draw("AC*");

        return 0;

}

