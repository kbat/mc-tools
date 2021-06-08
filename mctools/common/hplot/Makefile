.PHONY: all clean perf

all: hplot

ROOTCONFIG := root-config
#ARCH       := $(shell $(ROOTCONFIG) --arch)
#PLATFORM   := $(shell $(ROOTCONFIG) --platform)

ROOTCFLAGS := $(shell $(ROOTCONFIG) --cflags)
ROOTGLIBS  := $(shell $(ROOTCONFIG) --glibs)
ROOTLIBS   := $(shell $(ROOTCONFIG) --libs)
GCC         = g++

CXXFLAGS := -g -std=c++17 -Ofast -fno-math-errno -Wall

obj/%.o: src/%.cxx src/%.h
	@echo "Compiling $@"
	@$(GCC) -c $(CXXFLAGS) -Isrc/ $< $(ROOTCFLAGS) -o $@

obj/hplot.o: src/hplot.cxx
	@echo "Compiling $@"
	@$(GCC) -c $(CXXFLAGS) -Isrc/ $< $(ROOTCFLAGS) -o $@

obj/minimal.o: src/minimal.cxx
	@echo "Compiling $@"
	@$(GCC) -c $(CXXFLAGS) -Isrc/ $< $(ROOTCFLAGS) -o $@

obj/MainFrameDict.o: src/MainFrame.h src/MainFrameLinkDef.h
	@echo "Generating dictionary $@"
# use rootcint if going to run on travis. otherwise rootcline is better/newer
	@rootcling -f MainFrameDict.cxx -c $^
	@$(GCC) -c $(CXXFLAGS) -I./ MainFrameDict.cxx $(ROOTCFLAGS) -o $@

hplot: obj/hplot.o obj/Arguments.o obj/MainFrame.o obj/MainFrameDict.o obj/Data.o obj/Geometry.o obj/DynamicSlice.o
	@echo "Linking $@"
	@$(GCC) $^ $(ROOTLIBS) $(ROOTGLIBS) -lGeom -lboost_program_options -o $@

minimal: obj/minimal.o obj/Arguments.o obj/MainFrame.o obj/MainFrameDict.o obj/Data.o obj/Geometry.o
	@echo "Linking $@"
	@$(GCC) $^ $(ROOTLIBS) $(ROOTGLIBS) -lGeom -lboost_program_options -o $@
	valgrind --show-leak-kinds=all --leak-check=full --error-limit=no --gen-suppressions=all \
		./minimal /home/kbat/figs/TDC/runs/SpecF1.root 3>&1 1>&2 2>&3 | \
		grindmerge  > root-minimal.supp
	valgrind --show-leak-kinds=all --leak-check=full \
	        --suppressions=root-minimal.supp \
	        ./minimal /home/kbat/figs/TDC/runs/SpecF1.root

clean:
	@rm -fv hplot obj/*.o perf.data* perf.hist* obj/MainFrameDict.cxx obj/MainFrameDict_rdict.pcm minimal \
		MainFrameDict.cxx MainFrameDict_rdict.pcm \
		root-minimal.supp

perf: hplot
	rm -f perf.data
	perf record ./hplot
	sleep 5
	perf report

# https://root-forum.cern.ch/t/valgrind-and-root/28506
helgrind: hplot
	valgrind --tool=helgrind \
		--suppressions=$(shell root-config --etcdir)/helgrind-root.supp \
		./hplot a b c d

valgrind: hplot minimal
	valgrind --show-leak-kinds=all --leak-check=full \
		--suppressions=$(ROOTSYS)/etc/valgrind-root.supp \
	        --suppressions=root-minimal.supp \
		--track-origins=yes \
		./hplot /home/kbat/figs/TDC/runs/SpecF1-do-not-exist.root mesh25 c d
#	valgrind --tool=memcheck --track-origins=yes --show-leak-kinds=all \

	# valgrind --num-callers=30 --leak-check=full \
	# 	--suppressions=$(ROOTSYS)/etc/valgrind-root.supp \
	# 	root.exe myscript.C


sloc:
	sloccount src
