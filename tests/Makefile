.PHONY: run convert clean

all: convert

shield005.log: shield.inp
	$(FLUTIL)/rfluka -N0 -M5 shield.inp

shield.root: shield005.log
	fluka2root -f shield.inp

convert: shield.root

run: shield005.log

clean:
	@rm -frv fluka_* ranshi* *_fort* *_tab.* *_lis.* *_sum.* *.err *.log *.out shield-echo.inp shield.root
