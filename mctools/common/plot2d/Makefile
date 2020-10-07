.PHONY: all clean perf

all: plot2d

ROOTCONFIG := root-config
#ARCH       := $(shell $(ROOTCONFIG) --arch)
#PLATFORM   := $(shell $(ROOTCONFIG) --platform)

ROOTCFLAGS := $(shell $(ROOTCONFIG) --cflags)
ROOTGLIBS  := $(shell $(ROOTCONFIG) --glibs)
ROOTLIBS   := $(shell $(ROOTCONFIG) --libs)
GCC         = g++

CXXFLAGS := -g -Ofast -fno-math-errno -Wall

obj/%.o: src/%.cxx src/%.h
	@echo "Compiling $@"
	@$(GCC) -c $(CXXFLAGS) -Isrc/ $< $(ROOTCFLAGS) -o $@

obj/plot2d.o: src/plot2d.cxx
	@echo "Compiling $@"
	@$(GCC) -c $(CXXFLAGS) -Isrc/ $< $(ROOTCFLAGS) -o $@

obj/minimal.o: src/minimal.cxx
	@echo "Compiling $@"
	@$(GCC) -c $(CXXFLAGS) -Isrc/ $< $(ROOTCFLAGS) -o $@

obj/MainFrameDict.o: src/MainFrame.h src/MainFrameLinkDef.h
	@echo "Generating dictionary $@"
# rootcint is used due to old ROOT version @ travis. Better to use rootcling
	@rootcling -f MainFrameDict.cxx -c $^
	@$(GCC) -c $(CXXFLAGS) -I./ MainFrameDict.cxx $(ROOTCFLAGS) -o $@

plot2d: obj/plot2d.o obj/Arguments.o obj/MainFrame.o obj/MainFrameDict.o obj/Data.o
	@echo "Linking $@"
	@$(GCC) $^ $(ROOTLIBS) $(ROOTGLIBS) -lGeom -lboost_program_options -o $@

minimal: obj/minimal.o obj/Arguments.o obj/MainFrame.o obj/MainFrameDict.o obj/Data.o
	@echo "Linking $@"
	@$(GCC) $^ $(ROOTLIBS) $(ROOTGLIBS) -lGeom -lboost_program_options -o $@
	valgrind --show-leak-kinds=all --leak-check=full --error-limit=no --gen-suppressions=all \
		./minimal /home/kbat/figs/TDC/runs/SpecF1.root 3>&1 1>&2 2>&3 | \
		grindmerge  > root-minimal.supp
	valgrind --show-leak-kinds=all --leak-check=full \
	        --suppressions=root-minimal.supp \
	        ./minimal /home/kbat/figs/TDC/runs/SpecF1.root

clean:
	@rm -fv plot2d obj/*.o perf.data* perf.hist* obj/MainFrameDict.cxx obj/MainFrameDict_rdict.pcm minimal \
		MainFrameDict.cxx MainFrameDict_rdict.pcm \
		root-minimal.supp

perf: plot2d
	rm -f perf.data
	perf record ./plot2d
	sleep 5
	perf report

# https://root-forum.cern.ch/t/valgrind-and-root/28506
helgrind: plot2d
	valgrind --tool=helgrind \
		--suppressions=$(shell root-config --etcdir)/helgrind-root.supp \
		./plot2d a b c d

valgrind: plot2d minimal
	valgrind --show-leak-kinds=all --leak-check=full \
		--suppressions=$(ROOTSYS)/etc/valgrind-root.supp \
	        --suppressions=root-minimal.supp \
		--track-origins=yes \
		./plot2d /home/kbat/figs/TDC/runs/SpecF1-do-not-exist.root mesh25 c d
#	valgrind --tool=memcheck --track-origins=yes --show-leak-kinds=all \

	# valgrind --num-callers=30 --leak-check=full \
	# 	--suppressions=$(ROOTSYS)/etc/valgrind-root.supp \
	# 	root.exe myscript.C


sloc:
	sloccount src
