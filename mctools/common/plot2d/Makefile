.PHONY: all clean perf

all: plot2d

ROOTCONFIG :=   root-config
ARCH       :=   $(shell $(ROOTCONFIG) --arch)
PLATFORM   :=   $(shell $(ROOTCONFIG) --platform)

ROOTCFLAGS := $(shell $(ROOTCONFIG) --cflags)
ROOTGLIBS  := $(shell root-config --glibs)
ROOTLIBS   := $(shell root-config --libs)
OPT         = -g -Ofast -fno-math-errno -Wall
GCC         = clang++ -g

CXXFLAGS := -Ofast -fno-math-errno -std=c++17 -Wall

obj/plot2d.o: src/plot2d.cxx
	@echo "Compiling $@"
	$(GCC) -c $(CXXFLAGS) -Isrc/ $< $(ROOTCFLAGS) -o $@

plot2d: obj/plot2d.o
	@echo "Linking $@"
	$(GCC) $^ $(ROOTLIBS) -lGeom -lboost_program_options -o $@

clean:
	rm -fv plot2d obj/*.o perf.data* perf.hist*

perf: plot2d
	rm -f perf.data
	perf record ./plot2d
	sleep 5
	perf report

# https://root-forum.cern.ch/t/valgrind-and-root/28506
valgrind: plot2d
	valgrind --tool=helgrind --suppressions=$(ROOTSYS)/etc/helgrind-root.supp ./plot2d a b c d

	# valgrind --num-callers=30 --leak-check=full \
	# 	--suppressions=$(ROOTSYS)/etc/valgrind-root.supp \
	# 	root.exe myscript.C


sloc:
	sloccount src
