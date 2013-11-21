#! /usr/bin/python -W all
#
# Cell importance must always be defined
# Vacuum and BH are reserved names
# All cells are subtracted from the Vacuum geometry by the Geometry::Print method

from string import join
from sys import exit

class Material:
    """material"""
    def __init__(self, title, number):
        self.title = title
        self.number = number
        self.isotopes = {}
        self.p = 0

    def Add(self, m, p):
        self.isotopes[m] = p

    def Print(self, option):
        i = 0
        for m,p in self.isotopes.items():
            i = i+1
            if i==1:
                print "M%05i %s %f $ %s" % (self.number, m, p, self.title)
            else:
                print "       %s %f" % (m, p)


class Surface:
    """geometry surface
    """
    def __init__(self, number, trans, stype, equation, comment=None):
        self.number = number
        self.trans = trans
        self.stype = stype
        self.equation = equation
        self.comment = comment

    def Print(self, option):
        """Surface printer"""
        if option == 'mcnp':
            if self.trans:
                print("%04i %02i %s  %s" % (int(self.number), self.trans, self.stype.upper(), self.equation)),
            else:
                print("%04i    %s  %s " % (self.number, self.stype.upper(), self.equation)),
            if self.comment:
                print " "*10, "$ %s" % self.comment
            else: print

    def __str__(self):
        return str(self.number)

class Transformation:
    """transformation"""
    def __init__(self, title, number, unit, v1, v2, v3, b1, b2, b3, b4, b5, b6, b7, b8, b9, m=1):
        self.title = title
        self.number = number
        self.unit = unit
        if not unit in ['deg', 'cos']:
            print "Error in transformation %d: unit must be either 'deg' or 'cos', but not %s" % (number, unit)
        self.displacement = [v1, v2, v3]
        self.rotation = [b1, b2, b3, b4, b5, b6, b7, b8, b9]
        self.m = m

    def Print(self, option):
        """Transformation printer"""
        print "C %s" % self.title
        if option == 'mcnp':
            if self.unit is 'deg': 
                print "*TR%02i %s" % (self.number, join(map(str, self.displacement))),
            else:
                print "TR%02i %s" % (self.number, join(map(str, self.displacement))),
            print "       %s" % join(map(str, self.rotation[0:3])),
            print "       %s" % join(map(str, self.rotation[3:6])),
            print "       %s" % join(map(str, self.rotation[6:9]))

class Cell:
    """Cell"""
    def __init__(self, title, number):
        self.title = title
        self.number = number
        self.surfaces = []
        self.geometry = None
        self.transformation = None
        self.material = None
        self.density = None
        self.temperature = None
        self.imp = None

    def Surface(self, number, stype, equation, comment=None):
        """Transformation is not included since it is supposed to be unique for the region and managed by the appropriate method 'Transformation'
        """
        s = Surface(number, 0, stype, equation, comment)
        self.surfaces.append(s)
        return s

    def SetTransformation(self, t):
        """Sets the transformation for the region. It is supposed to be unique"""
        if self.transformation is not None: raise Exception("Transformation for cell %i ('%s') has already been defined!!!" % (self.number, self.title))

        self.transformation = t
        for s in self.surfaces:
            s.trans = t.number

    def PrintSurfaces(self, option):
        if self.surfaces: print "C ***", self.title.upper()
        for s in self.surfaces:
            s.Print(option)

    def PrintCell(self, option):
        if self.imp is None: raise Exception("Error: importance of the cell %i not defined" % self.number)
        if self.geometry is None: raise Exception("Geometry for cell %i is not defined" % self.number)

        print "C ***", self.title.upper()
        if self.material:
            print "%04d %05d %f %s" % (self.number, self.material.number, self.density, self.geometry)
        else: # vacuum
            print "%04d  0       %s" % (self.number, self.geometry)

        print "          IMP:%s" % self.imp
        if self.temperature: print "          TMP=%g" % self.temperature


    def __int__(self):
        return self.number



class Geometry:
    """geometry"""
    def __init__(self, title):
        self.title = title
        self.cells = []
        self.materials = []
#        self.surfaces = []
#        self.transformations = []


    # def Transformation(self, title, number, unit, v1, v2, v3, b1, b2, b3, b4, b5, b6, b7, b8, b9):
    #     t = Transformation(title, number, unit, v1, v2, v3, b1, b2, b3, b4, b5, b6, b7, b8, b9)
    #     self.transformations.append(t)
    #     return t
        
    # def Surface(self, number, trans, stype, equation, comment=None):
    #     s = Surface(number, trans, stype, equation, comment)
    #     self.surfaces.append(s)
    #     return s

    def AddCell(self, r):
        self.cells.append(r)

    def AddMaterial(self, m):
        self.materials.append(m)

    def Print(self, option):
        print self.title
        # Generate the list of non-vacuum and non-bh cells:
        non_vac_cells = []
        for r in self.cells:
            if r.title not in ['Vacuum', 'BH']:
                non_vac_cells.append(r)
        for r in self.cells:
            if r.title == 'Vacuum':
                for nvc in non_vac_cells: # todo: replace with lambda-loop
                    r.geometry = r.geometry + " #%04i" % nvc.number
            r.PrintCell(option)
        print
        for r in self.cells:
            r.PrintSurfaces(option)
        print
        for r in self.cells:
            if r.transformation:  r.transformation.Print(option)
        print "C *** MATERIALS ***"
        for m in self.materials:
            m.Print(option)
