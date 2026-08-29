.PHONY: all clean distclean test perf helgrind valgrind sloc FORCE

all: hplot

ROOTCONFIG := root-config
ROOTCFLAGS := $(shell $(ROOTCONFIG) --cflags)
ROOTGLIBS  := $(shell $(ROOTCONFIG) --glibs)
ROOTLIBS   := $(shell $(ROOTCONFIG) --libs)
CXX         = g++

# CSGEngine.cxx wraps the geoengine CSG library: csg.h/csgcontour.h declare
# the API, libgeoengine.a has the compiled definitions.  Fetched on demand
# from upstream rather than vendored - see the $(EXTDIR)/% rule below.
GEOENGINE_URL  := https://archive.fluka.eu/geoview
EXTDIR         := .extern
GEOENGINE_HDRS := $(EXTDIR)/csg.h $(EXTDIR)/csgcontour.h
GEOENGINE_LIB  := $(EXTDIR)/libgeoengine.a

# -Ofast would enable -ffast-math, which we do not want in a tool that
# computes and thresholds relative errors.  Override with e.g. make OPT=-O0
OPT       ?= -O2
CXXFLAGS  := -g $(OPT) -std=c++17 -fno-math-errno -pthread -Wall -Wextra -Isrc/ -I$(EXTDIR) -MMD -MP
LDLIBS    := $(ROOTLIBS) $(ROOTGLIBS) -lGeom -lboost_program_options -pthread

# Data used by the valgrind/minimal targets.  Override on the command line:
#   make valgrind TESTDATA=/path/to/file.root TESTHIST=mesh25
TESTDATA  ?= ../../../tests/hplot/test.root
TESTHIST  ?= h3

SRCS := $(wildcard src/*.cxx)
OBJS := $(patsubst src/%.cxx,obj/%.o,$(SRCS)) obj/MainFrameDict.o
DEPS := $(OBJS:.o=.d)

obj:
	@mkdir -p $@

$(EXTDIR):
	@mkdir -p $@

# Conditional GET: re-downloads only if the server's copy is newer than the
# local file's mtime, and -R stamps the local mtime from the server's
# Last-Modified header so the next run's comparison stays meaningful.  FORCE
# makes this recipe run on every invocation of make, but it only touches the
# target file - and so only triggers rebuilds of things depending on it -
# when the content actually changed.
FORCE:

$(EXTDIR)/%: FORCE | $(EXTDIR)
	@curl -fsSL -R -z $@ -o $@ $(GEOENGINE_URL)/$*

obj/%.o: src/%.cxx | obj
	@echo "Compiling $@"
	@$(CXX) -c $(CXXFLAGS) $(ROOTCFLAGS) $< -o $@

obj/CSGEngine.o: $(GEOENGINE_HDRS)

# The generated _rdict.pcm must sit next to the executable for the interpreter
# to find it at run time, so the dictionary is generated here rather than in obj/
MainFrameDict.cxx: src/MainFrame.h src/MainFrameLinkDef.h
	@echo "Generating dictionary $@"
	@rootcling -f $@ -c -Isrc/ $^

obj/MainFrameDict.o: MainFrameDict.cxx | obj
	@echo "Compiling $@"
	@$(CXX) -c $(CXXFLAGS) $(ROOTCFLAGS) $< -o $@

hplot: $(OBJS) $(GEOENGINE_LIB)
	@echo "Linking $@"
	@$(CXX) $^ $(LDLIBS) -o $@

test: hplot
	@cd ../../../tests/hplot && PATH=$(CURDIR):$$PATH python3 test.py

clean:
	@rm -fv hplot obj/*.o obj/*.d perf.data* perf.hist* \
		MainFrameDict.cxx MainFrameDict_rdict.pcm

distclean: clean
	@rm -rfv $(EXTDIR)

perf: hplot
	rm -f perf.data
	perf record ./hplot
	sleep 5
	perf report

# https://root-forum.cern.ch/t/valgrind-and-root/28506
helgrind: hplot
	valgrind --tool=helgrind \
		--suppressions=$(shell root-config --etcdir)/helgrind-root.supp \
		./hplot $(TESTDATA) $(TESTHIST)

valgrind: hplot
	valgrind --show-leak-kinds=all --leak-check=full \
		--suppressions=$(shell root-config --etcdir)/valgrind-root.supp \
		--track-origins=yes \
		./hplot $(TESTDATA) $(TESTHIST) -o /dev/null

sloc:
	sloccount src

-include $(DEPS)
