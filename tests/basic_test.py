#! /bin/python3

import os
import sys
import shutil
import tempfile

def test_dummy():
        print("test_dummy")
        val = 1
        assert val == 1

def test_root():
        # test whether ROOT is installed and compiled with Python support
        import ROOT

def test_import():
        # test whether the mctools module can be imported
        import mctools

def fluka2root(inp):
        tmpdir = tempfile.mkdtemp(suffix='.mc-tools')
        inpto = os.path.join(tmpdir, inp)
        shutil.copyfile(inp, inpto)

        os.chdir(tmpdir)

        cmd = "$FLUTIL/rfluka -N0 -M2 " + inp
        val = os.system(cmd)
        assert val == 0

        cmd = "fluka2root " + inp
        val = os.system(cmd)
        assert val == 0

        shutil.rmtree(tmpdir)

def test_fluka2root():
#        inpfrom = os.path.join(os.environ["FLUPRO"], inp)
#        inputs = ("example.inp", "exmixed.inp", "exdefi.inp", "exfixed.inp")
        inputs = ("shield.inp",)
        for inp in inputs:
                fluka2root(inp)


#fluka2root()
