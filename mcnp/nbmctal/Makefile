HOMEDIR:=$(PWD)
TMPDIR:=$(shell mktemp -d)

doc:    nbmctal2root.py  nbmctal.py nbmctaltest.py  nbroottest.py  nbroottestsuite.py  nbtestsuite.py
	(cat Doxyfile ; echo "INPUT = " $(ls $^)) | doxygen -

deb: mctal2root_1.0_all.deb

mctal2root_1.0_all.deb:	mctal2root.ctl nbmctal2root.py  nbmctal.py quick_guide.pdf
	echo $(TMPDIR)
	ln -s $(HOMEDIR)/mctal2root.ctl $(TMPDIR)/mctal2root.ctl
	ln -s $(HOMEDIR)/nbmctal2root.py $(TMPDIR)/nbmctal2root
	ln -s $(HOMEDIR)/nbmctal.py $(TMPDIR)/nbmctal.py
	ln -s $(HOMEDIR)/quick_guide.pdf $(TMPDIR)/quick_guide.pdf
	cd $(TMPDIR) && equivs-build mctal2root.ctl && mv *.deb $(HOMEDIR)
	@test -z $(TMPDIR) || rm -fr $(TMPDIR)

clean:
	rm -frv *~ latex html *.pyc doxygen.log *.deb