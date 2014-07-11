#!/usr/bin/env python

import sys, os, subprocess, sqlite3

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

# get the revision number of the WC using sqlite3
# prep = '_' if sys.platform == "win32" and os.getenv("SVN_ASP_DOT_NET_HACK") \
#        else '.'
# SVNWCDBPATH = prep + "svn/wc.db"
SVNWCDBPATH = ('_' if sys.platform == "win32" and
               os.getenv("SVN_ASP_DOT_NET_HACK") else '.') + "svn/wc.db"
curs = sqlite3.connect(SVNWCDBPATH).cursor()
rev = "r%d" % curs.execute("select MAX(revision) from NODES "
                           "where"
                           " presence IN ('normal', 'incomplete')"
                           " AND file_external is NULL"
                           " AND op_depth=0").fetchone()
setup(
    name = "mc_tools",
    version = rev,
    author = "Konstantin Batkov",
    author_email = "mc-tools@lizardie.com",
    url = "https://code.google.com/p/mc-tools/",
    license = "GNU General Public License, version 2",
    description = "Some Monte Carlo tools.",

    packages = find_packages(),
    # The 'install_requires' line commented because
    # 'installing numpy with easy_install fails for some reasons:
    #   Install numpy as a linux package or by using a windoze
    #   installer, or via pip, in advance to the installation of 
    #    mc-tools.
    # install_requires = [ "numpy" ],
    data_files = [
        # MCNP
        ("mcnp", [ "mcnp/AUTHORS",      "mcnp/ChangeLog",
                   "mcnp/configure.ac", "mcnp/Doxyfile",
                   "mcnp/Makefile.am",  "mcnp/mctal2root.ctl",
                   "mcnp/NEWS",         "mcnp/README",
                   "mcnp/reference_guide.pdf" ]),
        ("mcnp/examples",  [ "mcnp/examples/ssw2root/example.C" ]),
        # PHITS
        ("phits/examples", [ "phits/examples/loadlevel-single.job" ]),
        ("phits/elisp",    [ "phits/phits-mode.el" ])
    ],
    entry_points = {
        "console_scripts" : [
            # COMMON
            "ascii2gr     = common.ascii2gr:main",
            "ascii2th1    = common.ascii2th1:main",
            "ascii2th3    = common.ascii2th3:main",
            "ascii2tree   = common.ascii2tree:main",
            "h2ascii      = common.h2ascii:main",
            "hadd_av      = common.hadd_av:main",
            "scale_hist   = common.scale_hist:main",
            # FLUKA
            "usxsuw2txt   = fluka.usxsuw2txt:main",
            # MCNP
            "mcnp_source  = mcnp.mcnp_source:main",
            "mctaltest    = mcnp.mctaltest:main",
            "roottest     = mcnp.roottest:main",
            "ssw2root     = mcnp.ssw2root:main",
            "ssw2txt      = mcnp.ssw2txt:main",
            # PHITS
            "angel2root   = phits.angel2root:main",
            "rotate3dshow = phits.rotate3dshow:main",
            "wwinp2phits  = phits.wwinp2phits:main"
        ]
    },
    # other executable scripts
    scripts = [
        # COMMON
        "common/ll-self-submit.sh",
        # MCNP
        "mcnp/conversiontest.sh", "mcnp/loop_convert.sh",
        "mcnp/loop_test.sh",
        # PHITS
        "phits/epsout.sh", "phits/phits-set-n.sh",
        "phits/submit.py"
    ],
)
