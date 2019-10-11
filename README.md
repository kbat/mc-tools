# mc-tools
Some Monte Carlo tools for MCNPX, PHITS and FLUKA

Project homepage: https://github.com/kbat/mc-tools

* MСNРХ
  * **Note:** These tools are for MCNPX. MCNP6 is not fully supported since we do not use it for several reasons.
  * Emacs [syntax highlighting script](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/mcnpgen-mode.el) for MCNP
  * An implementation of application programming interface (API) to
    read tallies from **mctal** files into a
    [Tally](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/mctal.py)
    object. This API allows to convert **mctal** files into any
    format.  It should work with any tallies except of the kcode data
    and tallies with perturbation records. 
  * [mctal2root](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/mctal2root.py)
    script converts a mctal file into the [ROOT](http://root.cern.ch) format. The tallies are saved
    as [THnSparse](https://root.cern.ch/doc/master/classTHnSparse.html) histograms.
  * [mctal2txt](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/mctal2txt.py)
    script shows an example how to convert a mctal file into an easily parsable ASCII file.
  * WSSA file converters **(MCNP6 is not fully supported)**
    * [ssw2txt](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/ssw2txt.py)
      converter: it converts WSSA files produced by MCNP(X) into plain
      text. The comments in the script explain how to derive additional
      information (like particle type and surface crossed) from the
      WSSA records.
    * [ssw2root](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/ssw2root.py)
      converter: it converts WSSA files produced by MСNР(X) into a ROOT
      ntuple.
      The list of aliases defined in the tree can be printed
      by the TTree::GetListOfAliases()::Print()
      method. In particular, this list shows how to get particle type and surface number.
      [This macro](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/examples/ssw2root/example.C)
      shows several very simple examples how to analyse SSW files with
      ROOT.  
    The WSSA file format depends on the MCNPX version, and currently
    the script has been tested with versions 2.6.0, 26b and 2.7.0.
  * A Python module to calculate atomic fractions of isotopes in a
    mixture for the given volume fractions of materials. Some examples
    can be found in
    [mixtures.py](https://github.com/kbat/mc-tools/blob/master/mctools/common/mixtures.py). 
* PHITS
  * Emacs [syntax highlighting script](https://github.com/kbat/mc-tools/blob/master/mctools/phits/phits-mode.el) for [PHITS](http://phits.jaea.go.jp/).
  * ANGEL to [ROOT](http://root.cern.ch) converter (converts the PHITS
    output to ROOT) - most of the tallies are supported, but there are
    known bugs and limitations, should be used with care. 
  * A script
    [rotate3dshow.py](https://github.com/kbat/mc-tools/blob/master/mctools/phits/rotate3dshow.py)
    which allows to animate the output of the **t-3dshow** tally. It
    runs PHITS to generate many images, so one can get a rotating
    video of geometry setup. Example:
    [rotate3dshow.gif](http://mc-tools.googlecode.com/files/rotate3dshow.gif)
    (should be viewed with an image viewer which supports GIF
    animation).  A simplified version of this script with a detailed
    manual can be downloaded from the PHITS website:
    <http://phits.jaea.go.jp/examples.html> 
* FLUKA
  * Emacs [syntax highlighting script](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/fluka-mode.el) for [FLUKA](http://www.fluka.org).
  * [usbsuw2root](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/usbsuw2root.py) converter: it converts the USRBIN results into a TH3F histogram. Note that this tool does not directly convert the files produced by the USRBIN card, but these files must first be averaged by the $FLUTIL/usbsuw program. The resulting avereged file can be converted into ROOT by usbsuw2root. The $FLUTIL/usbsuw call is done automatically if the [fluka2root](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/fluka2root.py) general converter is used.
  * [usxsuw2root](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/usxsuw2root.py) converter: it converts the USRBDX results into a TH2F histogram. + see the comments for the previous item.
  * [ustsuw2root](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/ustsuw2root.py) converter: it converts the USRTRACK results into a TH1F histogram. + see the comments for ```usbsuw2root```.
  * [eventdat2root](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/eventdat2root.py) converter: it converts the EVENTDAT results into a TTree object.
  * [fluka2root](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/fluka2root.py) converter. We believe it's convenient to call all the previous converters from the [fluka2root](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/fluka2root.py) script. In order to understand how it works, run ```$FLUTIL/rfluka -N0 -M3 $FLUPRO/exmixed.inp``` and then execute ```fluka2root exmixed.inp```. It creates a single ROOT file out of all FLUKA-produced data files converted into the ROOT histograms or trees.
* Generic tools
  * A Python module to calculate atomic fractions of isotopes in a
    mixture for the given volume fractions of materials. Some examples
    can be found in
    [mixtures.py](https://github.com/kbat/mc-tools/blob/master/mctools/common/mixtures.py). 
   * [ace2root](https://github.com/kbat/mc-tools/blob/master/mctools/common/ace2root.py), a converter from ACE to ROOT formats. Loops through all available cross-sections in an ACE file and saves them as TGraph objects. We use this simple script to visualise [ENDF](http://www.nndc.bnl.gov/exfor/endf00.jsp) cross sections. Requires the [PyNE](http://pyne.io) toolkit to be installed.

## Requirements ##
* If you are going to use the ROOT-related scripts (file names end with ```*2root```), you need to have [ROOT](http://root.cern.ch) to be compiled with Python support. In order to check whether the Python
   support in ROOT is set up correctly, say   
   ```import ROOT```  
   in the Python shell. You should not see any error messages. Python 3 can be used, but the ```fluka2root``` converter requires ROOT to be compiled with Python 2. These ```cmake``` arguments allow to select Python 2 for ROOT:  
```cmake  -DPYTHON_EXECUTABLE="/usr/bin/python" -Dpython="ON" -Dpython3="OFF" /path/to/root/source```
* If you are going to use the ```ace2root``` converter, you also need to have the [PyNE](http://pyne.io) toolkit to be installed.
* If the [GNU parallel](https://www.gnu.org/software/parallel) tool is installed then the FLUKA merge and ROOT converter tools called by the ```fluka2root``` script will be executed in parallel which makes it run faster.
* Linux and MacOS are supported. We have never tried to use these tools on Windows.

## Installation ##
```mc-tools``` can be installed either with the python package installer [pip](https://pip.pypa.io/en/stable) or manually by cloning the code and setting the appropriate variables.
The pip-based installation is recommended if you just intend to use the package, while the manual installation is recommended for developers.

### Installation with pip ###
In order to use [pip](https://pip.pypa.io/en/stable), you need to have [git](https://git-scm.com) as well as the **python-setuptools** and **python-pip** modules installed on your system.

```pip install git+https://github.com/kbat/mc-tools.git```

You will probably have to add the ```~/.local/bin``` folder into ```$PATH```. Read the output generated by ```pip```.

Uninstall: ```pip uninstall mc-tools```.

### Developer installation ###

1. Get the source code: 
    - either
```git clone https://github.com/kbat/mc-tools.git```
    - or download and uncompress ```https://github.com/kbat/mc-tools/archive/master.zip```
2. Set the variable MCTOOLS to the folder where you have installed the
   code:   
```export MCTOOLS=/path/to/mc-tools```
3. Add the ```$MCTOOLS``` folder into ```$PYTHONPATH```:  
```export PYTHONPATH=$MCTOOLS:$PYTHONPATH```
4. Add the ```$MCTOOLS/bin``` folder into your ```$PATH```:  
``` export PATH=$MCTOOLS/bin:$PATH ```


### Contacts ###
e-mail: `batkov [аt] gmail.com`

List of authors: Nicolò Borghi, Kazuyoshi Furutaka, Konstantin Batkov

### See also ###
http://pyne.io

https://github.com/SAnsell/CombLayer
