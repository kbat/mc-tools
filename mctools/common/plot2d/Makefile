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

obj/MainFrameDict.o: src/MainFrame.h src/MainFrameLinkDef.h
	@echo "Generating dictionary $@"
# rootcint is used due to old ROOT version @ travis. Better to use rootcling
	@rootcint -f obj/MainFrameDict.cxx -c $^
	@$(GCC) -c $(CXXFLAGS) -I./ obj/MainFrameDict.cxx $(ROOTCFLAGS) -o $@

plot2d: obj/plot2d.o obj/Arguments.o obj/MainFrame.o obj/MainFrameDict.o obj/Data.o
	@echo "Linking $@"
	@$(GCC) $^ $(ROOTLIBS)  $(ROOTGLIBS) -lGeom -lboost_program_options -o $@

minimal: src/minimal.cxx  obj/Arguments.o obj/MainFrame.o obj/MainFrameDict.o obj/Data.o
	$(GCC) $^ $(CXXFLAGS) $(ROOTCFLAGS) $(ROOTLIBS) $(ROOTGLIBS) -lGeom -lboost_program_options -o $@
	valgrind --show-leak-kinds=all --leak-check=full --error-limit=no --gen-suppressions=all --log-file=/tmp/root-minimal.log ./minimal 3>&1 1>&2 2>&3
	grindmerge < /tmp/root-minimal.log > root-minimal.supp
	valgrind --show-leak-kinds=all --leak-check=full \
	        --suppressions=root-minimal.supp \
	        ./minimal

clean:
	@rm -fv plot2d obj/*.o perf.data* perf.hist* obj/MainFrameDict.cxx obj/MainFrameDict_rdict.pcm minimal

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
		./plot2d a b c d
#	valgrind --tool=memcheck --track-origins=yes --show-leak-kinds=all \

	# valgrind --num-callers=30 --leak-check=full \
	# 	--suppressions=$(ROOTSYS)/etc/valgrind-root.supp \
	# 	root.exe myscript.C


sloc:
	sloccount src
