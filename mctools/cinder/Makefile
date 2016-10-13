CXXFLAGS  := -Wall -fPIC
ROOTFLAGS := `root-config --cflags --glibs`

all: libAlltabs.so

alltabsDict.cc:  Nuclide.hh Table.hh LinkDef.h
	@echo "Generating dictionary $@..."
	@rootcint -f $@ -c $^

libAlltabs.so: Table.cc Nuclide.cc alltabsDict.cc
	@echo "Compiling $@"
	@g++ -shared $(CXXFLAGS) $^ -o $@ $(ROOTFLAGS)

clean:
	@rm -fv libAlltabs.so
	@rm -fv alltabsDict.*
