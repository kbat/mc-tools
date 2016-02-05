### Commented entries have reasonable defaults.
### Uncomment to edit them.
Source: mctal2root
Section: misc
Priority: optional
Homepage: https://github.com/kbat/mc-tools
Standards-Version: 3.9.2

Package: mctal2root
Version: 1.0
Maintainer: Nicolò Borghi <borghi.nicolo@gmail.com>
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
Files: mctal2root /usr/local/bin
   mctal.py @pythondir@
Description: mctal to root converter
 A tool to convert mctal files produced by MCNP(X) into the ROOT format.
