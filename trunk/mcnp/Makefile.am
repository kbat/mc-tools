HOMEDIR:=$(PWD)
TMPDIR:=$(shell mktemp -d)

bin_SCRIPTS = mctal2root
CLEANFILES = $(bin_SCRIPTS)
EXTRA_DIST = mctal2root.py
mctal2root_PYTHON = mctal2root.py mctal.py
mctal2rootdir=$(pythondir)

do_substitution = sed -e 's,[@]pythondir[@],$(pythondir),g' -e 's,[@]PACKAGE[@],$(PACKAGE),g' -e 's,[@]VERSION[@],$(VERSION),g' 


mctal2root: mctal2root.py Makefile
	$(do_substitution) < mctal2root.py > mctal2root
	chmod +x mctal2root


doc:    mctal2root.py  mctal.py mctaltest.py  nbroottest.py  nbroottestsuite.py  nbtestsuite.py
	(cat Doxyfile ; echo "INPUT = " $(ls $^)) | doxygen -

deb: mctal2root_1.0_all.deb

mctal2root_1.0_all.deb:	mctal2root.ctl mctal2root.py  mctal.py
	echo $(TMPDIR)
	ln -s $(HOMEDIR)/mctal2root.ctl $(TMPDIR)/mctal2root.ctl
	ln -s $(HOMEDIR)/mctal2root.py $(TMPDIR)/mctal2root
	ln -s $(HOMEDIR)/mctal.py $(TMPDIR)/mctal.py
	cd $(TMPDIR) && equivs-build mctal2root.ctl && mv *.deb $(HOMEDIR)
	@test -z $(TMPDIR) || rm -fr $(TMPDIR)

changelog:
	svn2cl

clean:
	rm -frv *~ latex html *.pyc doxygen.log *.deb