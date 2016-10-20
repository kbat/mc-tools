CXXFLAGS  := -Wall -fPIC
ROOTFLAGS := `root-config --cflags --glibs`

all: alltabs2ttree

alltabsDict.cxx:  TNuclide.h TTable.h LinkDef.h
	@echo "Generating dictionary $@..."
	@rootcint -f $@ -c $^

libAlltabs.so: TTable.cxx TNuclide.cxx alltabsDict.cxx
	@echo "Compiling $@"
	@g++ -shared $(CXXFLAGS) $^ -o $@ $(ROOTFLAGS)

alltabs2ttree: libAlltabs.so alltabs2ttree.cxx
	@echo "Compiling1 $@"
	g++ $^ -Wall -g $(ROOTFLAGS) -L./ -lAlltabs -o $@


clean:
	@rm -fv libAlltabs.so
	@rm -fv alltabsDict.*
	@rm -fv alltabs2ttree
