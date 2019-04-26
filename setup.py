#!/usr/bin/env python

from __future__ import print_function
import sys, os, subprocess

# prepare setuptools environment
try:
    from setuptools import setup, find_packages
except ImportError:
    print("Could NOT import setuptools, try ez_setup...")
    try:
        from ez_setup import use_setuptools
        use_setuptools()
        from setuptools import setup, find_packages
    except ImportError:
        print("Could NOT import either setuptools or ez_setup, GIVE UP!")
        print("Download ez_setup.py e.g. " \
            "from https://bootstrap.pypa.io/ez_setup.py,")
        print("place it in the same directory as setup.py, and try again... ")
        sys.exit(1)

setup(
    name = "mc-tools",
    version = os.popen("git describe --tags --long").read().strip(),
    author = "Konstantin Batkov",
    author_email = "batkov@gmail.com",
    url = "https://github.com/kbat/mc-tools/",
    license = "BSD License",
    description = "Some Monte Carlo tools",

    packages = find_packages(),
    # The 'install_requires' line commented because
    # 'installing numpy with easy_install fails for some reasons:
    #   Install numpy as a linux package or by using a windoze
    #   installer, or via pip, in advance to the installation of 
    #    mc-tools.
    # install_requires = [ "numpy" ],
    data_files = [
        # MCNP
        ("mcnp", [ "mctools/mcnp/AUTHORS",      "mctools/mcnp/ChangeLog",
                   "mctools/mcnp/configure.ac", "mctools/mcnp/Doxyfile",
                   "mctools/mcnp/Makefile.am",  "mctools/mcnp/mctal2root.ctl",
                   "mctools/mcnp/NEWS",         "mctools/mcnp/README",
                   "mctools/mcnp/reference_guide.pdf" ]
        ),
        ("mctools/mcnp/examples",
         [ "mctools/mcnp/examples/ssw2root/example.C" ]
        ),
        # PHITS
        ("mctools/phits/examples",
         [ "mctools/phits/examples/loadlevel-single.job" ]
        ),
        ("mctools/phits/elisp",
         [ "mctools/phits/phits-mode.el" ]
        ),
        # FLUKA
        ("mctools/fluka/elisp",
         ["mctools/fluka/fluka-mode.el"]
        )
    ],
    entry_points = {
        "console_scripts" : [
            # COMMON
            "ascii2gr     = mctools.common.ascii2gr:main",
            "ascii2th1    = mctools.common.ascii2th1:main",
            "ascii2th3    = mctools.common.ascii2th3:main",
            "ascii2tree   = mctools.common.ascii2tree:main",
            "h2ascii      = mctools.common.h2ascii:main",
            "hadd_av      = mctools.common.hadd_av:main",
            "scale_hist   = mctools.common.scale_hist:main",
            # FLUKA
            "usxsuw2txt   = mctools.fluka.usxsuw2txt:main",
            # MCNP
            "mcnp_source  = mctools.mcnp.mcnp_source:main",
            "mctal2root   = mctools.mcnp.mctal2root:main",
            "ssw2root     = mctools.mcnp.ssw2root:main",
            "ssw2txt      = mctools.mcnp.ssw2txt:main",
            # PHITS
            "angel2root   = mctools.phits.angel2root:main",
            "rotate3dshow = mctools.phits.rotate3dshow:main",
            "wwinp2phits  = mctools.phits.wwinp2phits:main"
        ]
    },
    # other executable scripts
    scripts = [
        # COMMON
        "mctools/common/ll-self-submit.sh",
        # MCNP
        "mctools/mcnp/conversiontest.sh", "mctools/mcnp/loop_convert.sh",
        "mctools/mcnp/loop_test.sh",
        # PHITS
        "mctools/phits/epsout.sh", "mctools/phits/phits-set-n.sh",
        "mctools/phits/submit.py"
    ],
)
