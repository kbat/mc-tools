#!/usr/bin/env python

import sys, os, subprocess

# prepare setuptools environment
try:
    from setuptools import setup, find_packages
except ImportError:
    print "Could NOT import setuptools, try ez_setup..."
    try:
        from ez_setup import use_setuptools
        use_setuptools()
        from setuptools import setup, find_packages
    except ImportError:
        print "Could NOT import either setuptools or ez_setup, GIVE UP!"
        print "Download ez_setup.py e.g. " \
            "from https://bootstrap.pypa.io/ez_setup.py,"
        print "place it in the same directory as setup.py, and try again... "
        sys.exit(1)

setup(
    name = "mc_tools",
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
        ("mcnp", [ "mc_tools/mcnp/AUTHORS",      "mc_tools/mcnp/ChangeLog",
                   "mc_tools/mcnp/configure.ac", "mc_tools/mcnp/Doxyfile",
                   "mc_tools/mcnp/Makefile.am",  "mc_tools/mcnp/mctal2root.ctl",
                   "mc_tools/mcnp/NEWS",         "mc_tools/mcnp/README",
                   "mc_tools/mcnp/reference_guide.pdf" ]),
        ("mc_tools/mcnp/examples",
         [ "mc_tools/mcnp/examples/ssw2root/example.C" ]),
        # PHITS
        ("mc_tools/phits/examples",
         [ "mc_tools/phits/examples/loadlevel-single.job" ]),
        ("mc_tools/phits/elisp",
         [ "mc_tools/phits/phits-mode.el" ])
    ],
    entry_points = {
        "console_scripts" : [
            # COMMON
            "ascii2gr     = mc_tools.common.ascii2gr:main",
            "ascii2th1    = mc_tools.common.ascii2th1:main",
            "ascii2th3    = mc_tools.common.ascii2th3:main",
            "ascii2tree   = mc_tools.common.ascii2tree:main",
            "h2ascii      = mc_tools.common.h2ascii:main",
            "hadd_av      = mc_tools.common.hadd_av:main",
            "scale_hist   = mc_tools.common.scale_hist:main",
            # FLUKA
            "usxsuw2txt   = mc_tools.fluka.usxsuw2txt:main",
            # MCNP
            "mcnp_source  = mc_tools.mcnp.mcnp_source:main",
            "ssw2root     = mc_tools.mcnp.ssw2root:main",
            "ssw2txt      = mc_tools.mcnp.ssw2txt:main",
            # PHITS
            "angel2root   = mc_tools.phits.angel2root:main",
            "rotate3dshow = mc_tools.phits.rotate3dshow:main",
            "wwinp2phits  = mc_tools.phits.wwinp2phits:main"
        ]
    },
    # other executable scripts
    scripts = [
        # COMMON
        "mc_tools/common/ll-self-submit.sh",
        # MCNP
        "mc_tools/mcnp/conversiontest.sh", "mc_tools/mcnp/loop_convert.sh",
        "mc_tools/mcnp/loop_test.sh",
        # PHITS
        "mc_tools/phits/epsout.sh", "mc_tools/phits/phits-set-n.sh",
        "mc_tools/phits/submit.py"
    ],
)
