#!/usr/bin/env python3
# order: WSF
# 2020-07-14    6 16 8  9 8 12
# 2020-09-09    6 16 8  9 8 12
# 2020-10-03    6 16 8  9 9 12
# 2020-10-27    6 18 8  9 9 12
# 2020-11-24    7 20 8  9 9 12
# 2020-12-01    7 21 10 9 9 12
# 2020-12-07    7 22 10 9 9 12
# 2021-02-01    7 22 10 9 10 12
# 2021-03-29    7 21 10 9 10 12
# 2021-04-01    8 21 10 9 10 12
# 2021-06-14    8 21 10 9 10 13
# 2021-08-17    8 23 10 10 10 13
# 2022-02-10    8 23 10 10 10 12
# 2022-03-14    8 23 11 10 10 12
# 2022-03029    8 24 11 10 10 12

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
    name = "mc_tools",
    version = os.popen("git describe --tags --long").read().strip(),
    author = "Konstantin Batkov",
    author_email = "batkov@gmail.com",
    url = "https://github.com/kbat/mc-tools/",
    license = "LGPL-3.0 License",
    description = "Some Monte Carlo tools for MCNPX, PHITS and FLUKA",

    packages = find_packages(),

    install_requires = [ "numpy",
                         "pandas"
    ],

    data_files = [
        # MCNP
        ("mctools/mcnp", [ "mctools/mcnp/reference_guide.pdf" ]
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
            "ace2root     = mctools.common.ace2root:main",
            "ascii2gr     = mctools.common.ascii2gr:main",
            "ascii2th1    = mctools.common.ascii2th1:main",
            "ascii2th3    = mctools.common.ascii2th3:main",
            "ascii2tree   = mctools.common.ascii2tree:main",
            "h2ascii      = mctools.common.h2ascii:main",
            "vtk2root     = mctools.common.vtk2root:main",
            "lsroot       = mctools.common.lsroot:main",
            "plot2d       = mctools.common.plot2d:main",
            "root2txt     = mctools.common.root2txt:main",
            # FLUKA
            "fluka2root    = mctools.fluka.fluka2root:main",
            "eventdat2root = mctools.fluka.eventdat2root:main",
            "plotgeom2root = mctools.fluka.plotgeom2root:main",
            "usbsuw2root   = mctools.fluka.usbsuw2root:main",
            "ustsuw2root   = mctools.fluka.ustsuw2root:main",
            "usxsuw2root   = mctools.fluka.usxsuw2root:main",
            # MCNP
            "mctal2root   = mctools.mcnp.mctal2root:main",
            "ssw2root     = mctools.mcnp.ssw2root:main",
            "ssw2txt      = mctools.mcnp.ssw2txt:main",
            "mcnpview     = mctools.mcnp.mcnpview:main",
            "mcnpxview    = mctools.mcnp.mcnpview:main",
            # PHITS
            "angel2root   = mctools.phits.angel2root:main",
            "rotate3dshow = mctools.phits.rotate3dshow:main",
        ]
    },

    scripts = [
        "bin/mc-tools-fluka-merge",
        "bin/fluka.stop",
        "bin/rfluka.stop",
    ]
)
