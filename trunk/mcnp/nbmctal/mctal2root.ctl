### Commented entries have reasonable defaults.
### Uncomment to edit them.
Source: mctal2root
Section: misc
Priority: optional
Homepage: http://code.google.com/p/mc-tools
Standards-Version: 3.9.2

Package: mctal2root
Version: 1.0
Maintainer: Nicolò Borghi <nicolo.borghi@email.com>
# Pre-Depends: <comma-separated list of packages>
# Depends: <comma-separated list of packages>
# Recommends: <comma-separated list of packages>
# Suggests: <comma-separated list of packages>
# Provides: <comma-separated list of packages>
# Replaces: <comma-separated list of packages>
# Architecture: all
# Copyright: <copyright file; defaults to GPL2>
# Changelog: <changelog file; defaults to a generic changelog>
# Readme: README.Debian
# Extra-Files: quick_guide.pdf README
Files: nbmctal2root /usr/local/bin/nbmctal2root
   nbmctal.py /usr/lib/pymodules/python2.7
Description: mctal to root converter
 A tool to convert mctal files produced by MCNP(X) into the ROOT format.
