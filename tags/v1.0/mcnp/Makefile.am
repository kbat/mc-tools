bin_SCRIPTS = mctal2root
CLEANFILES = $(bin_SCRIPTS)
EXTRA_DIST = mctal2root.py
mctal2root_PYTHON = mctal2root.py mctal.py
mctal2rootdir=$(pythondir)

do_substitution = sed -e 's,[@]pythondir[@],$(pythondir),g' -e 's,[@]PACKAGE[@],$(PACKAGE),g' -e 's,[@]VERSION[@],$(VERSION),g' 


mctal2root: mctal2root.py Makefile.am configure
	@$(do_substitution) < mctal2root.py > mctal2root
	@chmod +x mctal2root

mctal2root.ctl.local: mctal2root.ctl
	@$(do_substitution) < mctal2root.ctl > mctal2root.ctl.local

doc:    mctal2root.py  mctal.py mctaltest.py  roottest.py  roottestsuite.py  testsuite.py
	(cat Doxyfile ; echo "INPUT = " $(ls "$^")) | doxygen -

deb: mctal2root_1.0_all.deb

mctal2root_1.0_all.deb:	mctal2root mctal.py mctal2root.ctl.local
	equivs-build mctal2root.ctl.local

changelog:
	svn2cl

configure:
	aclocal
	autoconf
	automake --add-missing -Wno-portability

clean:
	rm -frv configure *~ latex html *.pyc doxygen.log *.deb mctal2root.ctl.local config.status config.log mctal2root Makefile.in
