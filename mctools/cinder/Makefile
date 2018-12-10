CXXFLAGS  := -Wall -fPIC
ROOTFLAGS := $(shell root-config --cflags --glibs)
ROOT_LIBDIR := $(shell root-config --libdir)
ROOT_BINDIR := $(shell root-config --bindir)

all: alltabs2ttree

libAlltabsDict.cxx:  ./include/TNuclide.h ./include/TTable.h ./include/LinkDef.h
	@echo "Generating dictionary $@..."
	@rootcling -f $@ -rmf libAlltabs.rootmap -rml libAlltabs -s libAlltabs $^
	@mkdir -p ./lib
	@mv libAlltabs.rootmap ./lib
	@mv libAlltabs_rdict.pcm ./lib

libAlltabs.so: ./src/TTable.cxx ./src/TNuclide.cxx libAlltabsDict.cxx
	@echo "Compiling $@"
	@g++ -shared $(CXXFLAGS) -I./include $^ -o $@ $(ROOTFLAGS)
	@mkdir -p ./lib
	@mv $@ ./lib

alltabs2ttree: libAlltabs.so ./src/alltabs2ttree.cxx
	@echo "Compiling $@"
	@g++ -I./include ./lib/$^ -Wall -g $(ROOTFLAGS) -L./lib -lAlltabs -o $@
	@mkdir -p ./bin
	@mv $@ ./bin

install: alltabs2ttree
	@echo "Installing libAlltabs.so, rootmap and pcm to $(ROOT_LIBDIR)"
	@install -C $(CURDIR)/lib/libAlltabs.rootmap $(ROOT_LIBDIR)/
	@install -C $(CURDIR)/lib/libAlltabs_rdict.pcm $(ROOT_LIBDIR)/
	@install -C $(CURDIR)/lib/libAlltabs.so $(ROOT_LIBDIR)/
	@echo "Installing alltabs2ttree to $(ROOT_BINDIR)"
	@install -C $(CURDIR)/bin/alltabs2ttree $(ROOT_BINDIR)/

uninstall:
	@echo "Uninstalling libAlltabs.so and alltabs2ttree"
	@rm -fv $(ROOT_LIBDIR)/libAlltabs.rootmap
	@rm -fv $(ROOT_LIBDIR)/libAlltabs_rdict.pcm
	@rm -fv $(ROOT_LIBDIR)/libAlltabs.so
	@rm -fv $(ROOT_BINDIR)/alltabs2ttree

clean:
	@rm -fv ./lib/libAlltabs_rdict.pcm
	@rm -fv ./lib/libAlltabs.rootmap
	@rm -fv ./lib/libAlltabs.so
	@rm -fv libAlltabsDict.cxx
	@rm -fv ./bin/alltabs2ttree
	@rm -rfv ./lib
	@rm -rfv ./bin


