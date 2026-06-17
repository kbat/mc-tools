from functools import lru_cache
import ctypes
import sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True


vals = []
errs = []

class Value:
        def __init__(self, val, err, bin):
                self.val = val
                self.err = err
                self.relerr = 100.0 # \percent
                if val >= 1.0e-20:
                        self.relerr = 100.0*err/val
                self.bin = bin

        def __gt__(self, other):
                if (isinstance(other, Value)):
                        return self.val > other.val
                return NotImplemented

        def __str__(self):
                return f"{self.val:.3g} ± {self.err:.1g}   {self.relerr:.1f} %"



class Zone:
        def __init__(self, name, title, hist, area, xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None):
                for coord, lo, hi in (('x', xmin, xmax), ('y', ymin, ymax), ('z', zmin, zmax)):
                        if (lo is None) != (hi is None):
                                raise ValueError(f"Zone '{name}': {coord}min and {coord}max must both be set or both be unset")
                self.name = name
                self.title = title
                self.xmin, self.xmax = xmin, xmax
                self.ymin, self.ymax = ymin, ymax
                self.zmin, self.zmax = zmin, zmax
                self.hist = hist
                self.area = area # container area
                self.value = self.calculate()

        @lru_cache(maxsize=None)
        def calculate(self):
                eps = 1e-3
                for axis, lo, hi in ((self.hist.GetXaxis(), self.xmin, self.xmax),
                                     (self.hist.GetYaxis(), self.ymin, self.ymax),
                                     (self.hist.GetZaxis(), self.zmin, self.zmax)):
                        if lo is not None:
                                if abs(lo - hi) < eps:
                                        lo, hi = lo - eps, hi + eps
                                axis.SetRangeUser(lo, hi)
                b = self.hist.GetMaximumBin()
                val = self.hist.GetBinContent(b)
                err = self.hist.GetBinError(b)

                for axis in (self.hist.GetXaxis(), self.hist.GetYaxis(), self.hist.GetZaxis()):
                    axis.SetRange()

                # if val < 1e-6:
                #         print(self.full_name, val, file=sys.stderr)
                return Value(val, err, b)

        def getValue(self):
                return self.value

        @property
        def full_name(self):
                return f"{self.area.full_name}.{self.name}"

        def Print(self):
                m = self.getValue()
                i,j,k = ctypes.c_int(0),ctypes.c_int(0),ctypes.c_int(0)
                b = m.bin
                self.hist.GetBinXYZ(b, i,j,k)
                x = self.hist.GetXaxis().GetBinCenter(i.value)
                y = self.hist.GetYaxis().GetBinCenter(j.value)
                z = self.hist.GetZaxis().GetBinCenter(k.value)

                print(f"{self.title}: {m}\t coordinates: {x:.4f} {y:.4f} {z:.4f} \t {self.full_name}")

                # print > 0.5 uSv/h in stderr:
                if m.val > 0.5 and not self.title.strip().startswith("One"):
                        print(f"\033[31m Above 0.5 µSv/h: \033[0m {self.title}: {m}", file=sys.stderr)

                vals.append(m.val)
                errs.append(m.relerr)

class Area:
        """ Area - a container for zones

        0m, 1m, Bulk, Duct, Max
        """
        def __init__(self, name, title, region, getHist=None):
                self.name = name
                self.title = title
                self.zones = []
                self.isVirtual = False # if true then just a collection of already existing zones for max calculation
                self.region = region # containing region
                self._getHist = getHist

        def checkZoneName(self, name):
                if name in [z.name for z in self.zones]:
                        print(f"Error: zone {name} already exists", file=sys.stderr)
                        sys.exit(1)

        def addZone(self, name, title, xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None, hist=None):
                self.checkZoneName(name)
                if isinstance(hist, str):
                        if self._getHist is None:
                                raise RuntimeError(
                                        f"addZone '{name}': hist={hist!r} is a string but no getHist "
                                        f"callable was provided to Region/Area"
                                )
                        hist = self._getHist(hist)
                z = Zone(name, title, hist if hist is not None else self.hist, self,
                         xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax)
                self.zones.append(z)
                return z

        def addZoneDefined(self, z, newName=None):
                """
                add already-defined zone into the zone list
                newName must be defined if a zone with z.name already exists
                """
                if newName != None:
                        new_zone = copy.copy(z)
                        new_zone.name = newName
                self.checkZoneName(new_zone.name)
                self.zones.append(new_zone)

        def addZoneMax(self, name="Max", zones=None, title=None):
                if zones is None: # use all zones
                        zones = [z.name for z in self.zones]
                        if title is None:
                                title = f" * Maximum over the whole {self.region.name}.{self.name} area"
                        return self.addZoneMax(name, zones, title)
                else: # use the specified zones only
                        if title is None:
                                title = " * Maximum of the " + " ".join([t for t in zones]) + " zones"
                        a = Area(name, title, self)
                        for name in zones:
                                z = self.getZone(name)
                                if z is None:
                                        print(f"Not found: {name}", file=sys.stderr)
                                        sys.exit(1)
                                a.zones.append(z)
                        self.zones.append(a)
                        a.isVirtual = True
                        return a

        def getZone(self, name):
                """ Return zone by its name """
                # generator expression:
                z = next((obj for obj in self.zones if obj.name == name), None)
                if z is None:
                        raise LookupError(f"Zone not found: {name}")
                return z


        def getValue(self):
                values = []
                for z in self.zones:
                        values.append(z.getValue())
                return max(values)

        @property
        def full_name(self):
                return f"{self.region.name}.{self.name}"

        def Print(self):
                if self.isVirtual:
                        print(f"{self.title}:", self.getValue())
                else:
                        for z in self.zones:
                                z.Print()

class Region:
        """ Region - a container for areas

        Inside, Klystron, AccessSide, Access, Roof, Outside, Max
        """
        def __init__(self, name, title, getHist=None):
                self.name = name
                self.title = title
                self.area = {}
                self._getHist = getHist

        def checkAreaName(self, name):
                if name in [n for n in self.area.keys()]:
                        print(f"Error: area {name} already exists", file=sys.stderr)
                        sys.exit(1)

        def addArea(self, name):
                self.checkAreaName(name)
                self.area[name] = Area(name, "", self, getHist=self._getHist)
                return self.area[name]

        def getArea(self, name):
                return self.area[name]

        def addAreaMax(self, name="Max"):
                areas = self.area.copy()
                self.checkAreaName(name)
                self.area[name] = Area(name, f"* Maximum over the whole {self.name} region", self)
                self.area[name].isVirtual = True
                for a in areas.values():
                        self.area[name].zones.append(a)

        def Print(self):
                print("#",self.title)
                for a in self.area.values():
                        a.Print()

class Scenario:
        """ Scenario - a container for configurations """
        def __init__(self, name):
                self.name = name
                self.configurations = []

        def addConfig(self, c):
                self.configurations.append(c)

        def getConfig(self, name):
                """ Return configuration by its name """
                # generator expression:
                c = next((obj for obj in self.configurations if obj.name == name), None)
                if c is None:
                        raise LookupError(f"Configuration not found: {name}")
                return c

        def getValue(self, config, region, area, zone):
                c = self.getConfig(config)
                r = c.getRegion(region)
                a = r.getArea(area)
                z = a.getZone(zone)
                return z.getValue()

        def setValue(self, config, region, area, zone, value):
                c = self.getConfig(config)
                r = c.getRegion(region)
                a = r.getArea(area)
                z = a.getZone(zone)
                z.value = value

        def Print(self, config, region, area, zone):
                val = self.getValue(config, region, area, zone)
                print(f"{self.name}.{config}.{region}.{area}.{zone}", val)


class Configuration:
        """ Configuration - beam loss config (1A, 2A, 2BA, 2BB etc)"""
        def __init__(self, name, rootfname=None, scalefname="scale.txt"):
                self.name = name
                self.regions = []

                if rootfname is None:
                        rootfname=name+".root"

                self.scale = self.getScale(scalefname)

                self._hists = {}
                self._rootfile = ROOT.TFile(rootfname)

        def getScale(self,fname):
            with open(fname) as f:
                return float(f.readline())

        def getHist(self, hname):
                """Load and cache a histogram from the ROOT file. Only valid during __init__."""
                if hname not in self._hists:
                        h = self._rootfile.Get(hname)
                        assert h, f"Histogram {hname} is not found in {self._rootfile.GetName()}"
                        h.Scale(self.scale)
                        h.SetDirectory(0)
                        self._hists[hname] = h
                return self._hists[hname]

        def addRegion(self, name, title):
                r = Region(name, title, getHist=self.getHist)
                self.regions.append(r)
                return r

        def getRegion(self, name):
                """ Return region by its name """
                # generator expression:
                r = next((obj for obj in self.regions if obj.name == name), None)
                if r is None:
                        raise LookupError(f"Region not found: {name}")
                return r

def getPrintedValue(val, err):
        """ Return a string with the value to be printed

        If value is zero, no error is printed
        """
        epsilon = 1e-10
        color=""
        bigerror=""
        if val > 0.25:
                color = "[color=abovequater]"
        if val > 0.5:
                color = "[color=abovehalf]"

        if abs(val) > epsilon and err/val > 0.2:
                bigerror=" \\bigerror"
        return "\\num{0.0}" if abs(val) < epsilon  else "\\num%s{%f +- %f}%s" % (color, val, err, bigerror)

def createMaxConfiguration(s):
        """ Create 'Max' configuration for the given scenario """
        cmax = copy.deepcopy(s.getConfig("1A"))
        cmax.name = "Max"
        s.addConfig(cmax)

        for c in s.configurations:
                if c.name == "Max":
                        continue
                for r in c.regions:
                        for a in r.area.keys():
                                for z in r.getArea(a).zones:
                                        vmax = s.getValue(cmax.name, r.name, a, z.name)
                                        v = s.getValue(c.name, r.name, a, z.name)
                                        if v>vmax:
                                                s.setValue(cmax.name, r.name, a, z.name, v)

def printRate(confnames, root="."):
        path = Path(root)

        all_confnames = list(confnames) + ["Max"]

        print("% This file is generated by getmax.py. Don't edit it by hand.")
        print("%")
        print("% Usage:")
        print("%    (let's assume this file is called 'rates.tex')")
        print(r"% 1. Load this file in your document preamble: \input{rates.tex}")
        print("% 2. If needed, redefine the 'abovequater' and 'abovehalf' colours as well as the 'bigerror' command after loading rates.tex. For instance:")
        print("% \\definecolor{abovequater}{HTML}{000000}")
        print("% \\definecolor{abovehalf}{HTML}{000000}")
        print("% \\renewcommand\\bigerror{}")
        print()
        print("\\definecolor{abovequater}{HTML}{ff8b00} % for dose rates > 0.25 uSv/h")
        print("\\definecolor{abovehalf}{HTML}{ff0000}   % for dose rates > 0.5 uSv/h")
        print("\\newcommand\\bigerror{\\textcolor{red}{(BIG ERROR!)}} % postfix for values with relative error above 20%")
        print("")
        print("\\NewDocumentCommand\\rate{mmmmg}{%")
        print("  % 1: scenario")
        print("  % 2: configuration")
        print("  % 3: region")
        print("  % 4: area")
        print("  % 5: zone")

        for folder in path.iterdir():
#                if not (folder.is_dir() and folder.name.startswith("conf-")):
                if not folder.name.startswith("conf-"):
                        continue
                sname = folder.name.removeprefix("conf-")
                print("% Scenario:", sname)

                s = Scenario(sname)
                for name in confnames:
                        rootfname = f"{folder}/{name}.root"
                        scalefname = f"{folder}/scale.txt"
                        c = Config(name, rootfname, "rghmesh", scalefname)
                        s.addConfig(c)

                createMaxConfiguration(s)

                print(r"  \\ifthenelse{\equal"+"{#1}{%s}}{" % sname, end="%\n")
                for cname in all_confnames:
                        print(r"    \\ifthenelse{\equal"+"{#2}{%s}}{" % cname, end="%\n")

                        c = s.getConfig(cname)
                        for r in c.regions:
                                print(r"      \\ifthenelse{\equal"+"{#3}{%s}}{" % r.name, end="%\n")
                                for a in r.area.keys():
                                        print(r"        \\ifthenelse{\equal"+"{#4}{%s}}{" % a, end="%\n")
                                        nspace = 10
                                        if a == 'Max':
                                                value = r.area[a].getValue()
                                                val = value.val
                                                err = value.err
                                                print(" "*nspace,"\\IfValueTF{#5}{\\textcolor{red}{Error: The Zone argument must be removed with the Max area}}{%s}" % getPrintedValue(val, err),
                                                      end=f"% {r.area[a].full_name}\n")
#                                                print(val, file=sys.stderr)
                                        else:
                                            for z in r.getArea(a).zones:
                                                    value = s.getValue(cname, r.name, a, z.name)
                                                    val = value.val
                                                    err = value.err
                                                    print(" "*nspace,r"\\ifthenelse{\equal"+"{#5}{%s}}{%s}{" % (z.name, getPrintedValue(val, err)),
                                                          end=f"% {z.full_name}\n")
                                                    nspace += 1
                                        print(" "*10,"}"*(nspace-10), end="%\n")
                                        print("        }{}%")
                                print("      }{}%")
                        print("    }{}%")
                print("    }{}%")
        print("}%")
