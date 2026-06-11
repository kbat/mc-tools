.PHONY: run clean convert test

all: test

rantest004:
	$(FLUPRO)/flutil/rfluka -e $(FLUPRO)/flukadpm3 -N0 -M3 test.inp
	@echo ""

run: rantest004

test.root:
	../../mctools/fluka/fluka2root.py -f -keep -userdump2root /home/kbat/usr/local/mc-tools/tests/fluka/userdump2root.sh test.inp

test.53.txt:
	(echo test.53.usrbin; echo -n ""; echo test.53.txt)| $(FLUPRO)/flutil/usbrea

test.54.txt:
	(echo test.54.usrbin; echo -n ""; echo test.54.txt)| $(FLUPRO)/flutil/usbrea

usrbin: test.53.txt test.54.txt

convert: run test.root usrbin

test: convert
	./test.py

clean:
	@rm -fv test00* rantest* test*usrbin test*usrbdx test*usrtrack test*resnuclei test*.lis test*.bnx test*.trk test*.bnn test*.rnc test*.dat test*.resnucle fort.* *.root draw.pdf test.54.txt
