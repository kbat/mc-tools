#! /usr/bin/python -W all

import sys, re, string
from math import *

try:
    from collections import OrderedDict as _default_dict
except ImportError:
    _default_dict = dict

AXES1D = ('eng', 'charge', 'mass', 'reg', 'x', 'y', 'z', 'r') # list of one-dimentional axes
AXES2D = ('chart', 'xy', 'yz', 'xz', 'rz') # list of two-dimentional axes

mcnp_phits_particles = {"n" : "neutron", "h":"proton", "/":"pion+ pion-", "z":"pion0", "d":"deuteron", "t":"triton", "s":"3he", "a":"alpha", "p":"photon", "e":"electron positron", "|":"muon+ muon-"}


def ReadSection(line):
    """ Section is a part of the ANGEL input file starting from alphabet characters with colon ':' line H:"""
    print "ReadSection", line
    sys.exit(0)

# exception classes
class Error(Exception):
    """Base class for ConfigParser exceptions."""

    def _get_message(self):
        """Getter for 'message'; needed only to override deprecation in
        BaseException."""
        return self.__message

    def _set_message(self, value):
        """Setter for 'message'; needed only to override deprecation in
        BaseException."""
        self.__message = value

    # BaseException.message has been deprecated since Python 2.6.  To prevent
    # DeprecationWarning from popping up over this pre-existing attribute, use
    # a new property that takes lookup precedence.
    message = property(_get_message, _set_message)

    def __init__(self, msg=''):
        self.message = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message

    __str__ = __repr__



class ParsingError(Error):
    """Raised when a configuration file does not follow legal syntax."""

    def __init__(self, filename):
        Error.__init__(self, 'File contains parsing errors: %s' % filename)
        self.filename = filename
        self.errors = []

    def append(self, lineno, line):
        self.errors.append((lineno, line))
        self.message += '\n\t[line %2d]: %s' % (lineno, line)

class MissingSectionHeaderError(ParsingError):
    """Raised when a key-value pair is found before any section header."""

    def __init__(self, filename, lineno, line):
        Error.__init__(
            self,
            'File contains no section headers.\nfile: %s, line: %d\n%r' %
            (filename, lineno, line))
        self.filename = filename
        self.lineno = lineno
        self.line = line


class TallyOutputParser:
    fname = None
    dict = _default_dict
    data = {}
    errors = {} # relative errors
    xarray = {} # array of x-boundaries
    subtitle = {} # array of subtitles

    nhist = 0 # number of histogram (appears in the histogram name)

    def __init__(self, fname):
        self.fname = fname
        self.file = open(fname)
        self.sections = self.dict()
        self.read()

    def has_section(self, section):
        return section in self.sections

    def has_option(self, section, option):
        return option in self.sections[section]

    def getSections(self):
        """ Return list of section names """
        return list(self.sections.keys())

    def FixSectName(self, sectionstr):
       return  sectionstr.replace(' ', '').lower()
       
    def is_1d(self, section):
        return self.get(section, 'axis') in AXES1D

    def is_2d(self, section):
        return self.get(section, 'axis') in AXES2D

# Regular expressions for parsing section headers and options:
# (borrowed from ConfigParser)

    SECTCRE = re.compile(
        r'\['                                 # [
        r'(?P<header>[^]]+)'                  # very permissive!
        r'\]'                                 # ]
        )
    OPTCRE = re.compile(
        r'(?P<option>[^:=\s][^:=]*)'          # very permissive!
        r'\s*(?P<vi>[:=])\s*'                 # any number of space/tab,
                                              # followed by separator
                                              # (either : or =), followed
                                              # by any # space/tab
        r'(?P<value>.*)$'                     # everything up to eol
        )

    
    def read(self):
        """
        Parse a sectioned setup file.

        The sections in setup file contains a title line at the top,
        indicated by a name in square brackets (`[]'), plus key/value
        options lines, indicated by `name = value' format lines.
        Blank lines, lines beginning with a '#', and just about everything else are ignored.
        """

        cursect = None                            # None, or a dictionary
        optname = None
        lineno = 0
        e = None                                  # None, or an exception
        axis = None

        isData = False # current line contains histogram data
        data = []    # list of data for the current histogram (not self.data)
        errors = []  # list of errors for the current histogram (not self.errors)
        xarray = []
        xarray_max = None # maximum boundary of array - appended after the loop
        isSubtitle = False # will be set to True when a line with 'newpage' is read, indicating that the next line is subtitle
        subtitle = ""

        while True:
            line = self.file.readline()
            if re.search("z: xorg", line): # !!! temprorary fix the 2D histogram titles
                break
            if not line:
                break
            lineno = lineno + 1
            line = line.strip()
            if isSubtitle:
                isSubtitle = False
                subtitle = line[1:].strip() # [1:] because the line starts with #

            if isSubtitle is False and re.search("newpage:", line):
                isSubtitle = True
            if line == '' or line[0] == '#':
                if isData  and line == '':
                    isData = False
                    print "data end"
                    self.data[self.nhist] = data[:] # [:] makes a slice (copy) of the tuple since we are going to delete it:
                    del data[:]
                    self.subtitle[self.nhist] = subtitle

                    if axis in AXES1D:
                        self.errors[self.nhist] = errors[:] # [:] makes a slice (copy) of the tuple since we are going to delete it:
                        del errors[:]
                        xarray.append(xarray_max)
                        self.xarray[self.nhist] = xarray[:]
                        del xarray[:]
                    self.nhist += 1
                continue
#            words = line.split()
#            for iw, w in enumerate(words):
#                if w == '#':
#                    line = string.join(words[:iw])
            
            mo = self.SECTCRE.match(line)
            if mo:
                sectname = mo.group('header')
#                print sectname
                if sectname in self.sections:
                    cursect = self.sections[sectname]
                else:
                    cursect = self.dict()
                    cursect['__name__'] = sectname
                    self.sections[sectname] = cursect
                    # So sections can't start with continuation line
                optname = None
            elif cursect is None:
                raise MissingSectionHeaderError(self.fname, lineno, line)
            else:
                mo = self.OPTCRE.match(line)
                if mo:
                    optname, vi, optval = mo.group('option', 'vi', 'value')
                    if vi in ('=', ':') and '#' in optval:
                        # '#' is a comment delimiter only if it follows
                        # a spacing character
                        pos = optval.find('#')
                        if pos != -1 and optval[pos-1].isspace():
                            optval = optval[:pos]
                    optval = optval.strip()
                        # allow empty values
                    if optval == '""':
                        optval = ''
                    optname = optname.lower().rstrip()
#                    try:
#                        cursect[optname]
#                    except KeyError:
#                        print "current section already has option ", optname
#                    else:
                    cursect[optname] = optval
                    # set the axis - we will need it below to parse the data format
                    if not axis and optname == 'axis':
                        axis = optval

                if re.search("^h", line) and not isData:
                    ReadSection(line)
                    print "data start"
                    isData = True
                    continue

                if isData:
                    print "data: ", line
                    words = line.split()
                    try:
                        float(words[0])
                    except ValueError:
#                        print "Ignoring line: ", line
                        continue
                    

                    if axis in AXES1D:
                        xarray.append(float(words[0]))
                        xarray_max = float(words[1])
                        data.append(float(words[2]))
                        errors.append(float(words[3]))
                    elif axis in AXES2D:
                        for w in words:
                            data.append(float(w))
                    # a non-fatal parsing error occurred.  set up the
                    # exception but keep going. the exception will be
                    # raised at the end of the file and will contain a
                    # list of all bogus lines
                    #if not e:
                    #    e = ParsingError(self.fname)
                    #e.append(lineno, repr(line))

  # if any parsing errors occurred, raise an exception
#        if e:
#            raise e
        print self.nhist, "histos found"
        print "xarray", self.xarray
        self.file.close()

    def get(self, section, option):
        if self.has_option(section, option):
            return self.sections[section][option]
        else:
            return None
#        opt = option.lower()
#        if section not in self.sections:
#            return "no such section"



class Input:
    inp = None
    pars = {} # dictionary of parameters

    def __init__(self, fname):
        self.inp = open(fname, 'w')

    def FixLine1(self, line):
        # we sort the dictionary by the key length, so we replace the longer keys first
        # in order avoid mistakes like AA = 5, AAB = 6 -> '5B'
        for key, value in sorted(self.pars.iteritems(), key=lambda(k,v):(len(k),v), reverse=True):
            line = line.replace("%s" % key, "%s" % str(value))

#            line = line.replace(" %s " % i, " %s " % str(self.pars[i]))
#            line = line.replace(" %s\n" % i, " %s\n" % str(self.pars[i]))
#            line = line.replace("(%s)" % i, "(%s)" % str(self.pars[i]))
#            line = line.replace("(%s " % i, "(%s " % str(self.pars[i]))
#            line = line.replace("-%s " % i, "-%s " % str(self.pars[i]))
        return line

    def FixLine(self, line):
        line1 = None
        while True:
            line1 = self.FixLine1(line)
            if line1 != line:
                line = line1
            else:
                return line

    def Line(self, line, comment=None):
        line = self.FixLine(line)
        if comment:
            line = line + " $ " + comment
        print >> self.inp, line

    def Section(self, sectname):
        self.Line('[%s]' % sectname)

    def Title(self, title):
        self.Line('[title]')
        self.Line(title)
        self.Line('')

    def End(self):
        self.Section('end')
        self.inp.close()

    def Set(self, name, value, comment=None):
        value_orig = value
        try:
            float(value)
        except ValueError:
            value = self.FixLine("%s" % value)
            eval(value)
            try:
                value = eval(value)
            except NameError:
                print "ERROR: cannot eval value '%s'" % value
                sys.exit(1)

        name = name.strip()
        self.pars[name] = value
        if value_orig != value:
            value_orig = value_orig + " = " + str(value)
        if comment: value_orig = str(value_orig) + "\t(%s)" % str(comment)
        print >> self.inp, "c %s = %s" % (name, value_orig)
        

    def Get(self, name):
        return self.pars[name]


