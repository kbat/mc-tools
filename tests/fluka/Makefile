.PHONY: run clean convert test

all: test

rantest004:
	$(FLUPRO)/flutil/rfluka -e $(FLUPRO)/flukadpm3 -N0 -M3 test.inp
	@echo ""

run: rantest004

test.root:
	fluka2root -f test.inp

convert: run test.root

test: convert
	./test.py

clean:
	rm -fv test00* rantest* test*usrbin test*usrbdx test*usrtrack test*resnuclei test.*lis fort.* *.root
