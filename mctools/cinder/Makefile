CXXFLAGS  := -Wall -fPIC
ROOTFLAGS := `root-config --cflags --glibs`

all: alltabs2ttree

alltabsDict.cc:  Nuclide.hh Table.hh LinkDef.h
	@echo "Generating dictionary $@..."
	@rootcint -f $@ -c $^

libAlltabs.so: Table.cc Nuclide.cc alltabsDict.cc
	@echo "Compiling $@"
	@g++ -shared $(CXXFLAGS) $^ -o $@ $(ROOTFLAGS)

alltabs2ttree: libAlltabs.so alltabs2ttree.cc
	@echo "Compiling1 $@"
	g++ $^ -Wall -g $(ROOTFLAGS) -L./ -lAlltabs -o $@


clean:
	@rm -fv libAlltabs.so
	@rm -fv alltabsDict.*
	@rm -fv alltabs2ttree
