#! /bin/python

import os
import sys
import shutil
import tempfile

def test_dummy():
        print("test_dummy")
        val = 1
        assert val == 1

def test_root():
        print("test root")
        pass

def fluka2root(inp):
        tmpdir = tempfile.mkdtemp(suffix='.mc-tools')
        inpfrom = os.path.join(os.environ["FLUPRO"], inp)
        inpto = os.path.join(tmpdir, inp)
        shutil.copyfile(inpfrom, inpto)

        os.chdir(tmpdir)

        cmd = "$FLUTIL/rfluka -N0 -M2 " + inp
        val = os.system(cmd)
        assert val == 0

        cmd = "fluka2root " + inp
        val = os.system(cmd)
        assert val == 0

        shutil.rmtree(tmpdir)

def test_fluka2root():
        for inp in ("example.inp", "exmixed.inp", "exdefi.inp", "exfixed.inp"):
                fluka2root(inp)
