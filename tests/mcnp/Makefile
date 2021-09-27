all: mctal convert

mctal: inp
	@mcnp6 i=inp
	@test -e mctal || (echo "Error: no mctal file produced"; exit 1)

convert: mctal
	@mctal2root mctal

xml: mctal
	@mctal2root mctal mctal.xml
	@bzip2 -9 mctal.xml

clean:
	@rm -fv *~ runtp? mdat? out? mctal mctal.root
