#How to install/uninstall mc-tools using PIP or SETUPTOOLS.

# Installation/Uninstallation using PIP #
`#` stands for the prompt for superuser, `$` that for ordinary user.

## Installation ##
```
# pip install http://mc-tools.googlecode.com/svn/trunk#egg=mc-tools
```
## List the installed files ##
```
$ pip show -f mc-tools
```
## Uninstallation ##
```
# pip uninstall mc-tools
```

If unfortunately the command above does **NOT** work, you may have to delete all the installed files _manually_...

# Installation/Uninstallation using SETUPTOOLS #
## Installation ##
After downloading the files with subversion and moving to the directory where the files reside, do the following:
```
# python setup.py install
```

If you wish, you can make a windows installer and install the tools using it;
```
$ python setup.py bdist_wininst
```
## Location of the installed files ##
All the python files in the package are in an egg directory; e.g.
/usr/lib/python2.7/site-packages/mc\_tools-[r241](https://code.google.com/p/mc-tools/source/detail?r=241)-py2.7.egg/
for Python 2.7 and mc-tools rev241.

Console scripts such as angel2root are in e.g. /usr/bin.
## Uninstallation ##
I (K.F) _believe_ you can delete the files by the following procedure;
  1. remove the console scripts listed in the 'entry\_points.txt' file in the egg directory,
  1. remove the egg directory itself.

# Installation/Uninstallation using windows installers created w/ SETUPTOOLS #
After downloading the files with subversion and moving to the directory where the files reside, do the following to create a windows installer:
```
# python setup.py bdist_wininst
```

The installer is in `dist` folder.  Install it.  Follow the usual procedure to uninstall it.