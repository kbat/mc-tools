# mc-tools
Some Monte Carlo tools for MCNP, MCNPX, PHITS and FLUKA

Project homepage: https://github.com/kbat/mc-tools

## MСNР
* Emacs [syntax highlighting script](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/mcnpgen-mode.el) for [MCNP](https://mcnp.lanl.gov).
* An implementation of application programming interface (API) to
    read data from **mctal** files. It allows to convert **mctal**
    files into any format. Known issue: tallies with perturbation
    records are not supported.
  * [mctal2root](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/mctal2root.py)
      script converts mctal to [ROOT](http://root.cern) format. The
      tallies are saved as
      [THnSparse](https://root.cern.ch/doc/master/classTHnSparse.html)
      histograms. The same script can convert mctal to XML format via [TXMLFile](https://root.cern.ch/doc/master/classTXMLFile.html).
  * [mctal2txt](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/mctal2txt.py)
      script shows an example how to convert an mctal file into an easily parsable ASCII file.
* WSSA file converters.
  * [ssw2txt](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/ssw2txt.py):
	  converts WSSA phase space files into plain text. The comments in
	  the script explain how to derive additional information (like
	  particle type and surface crossed) from the WSSA records.
  * [ssw2root](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/ssw2root.py):
      converts WSSA phase space files into a ROOT ntuple.  The list of
      aliases defined in the tree can be printed by the
      TTree::GetListOfAliases()::Print() method. In particular, this
      list shows how to get particle type and surface number.  [This
      macro](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/examples/ssw2root/example.C)
      gives several simple examples how to analyse SSW files with
      ROOT.
* [vol.py](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/vol.py):
    a tool to facilitate input of volume/importance/probability values
    for all cells in geometry. To be used with cards like **area**, **vol**, **imp**, **pd**, **dxc** etc.
	For example, in order to set the volume of cell 5 to 3.14, cell 7 to 2.71 in a geometry of 10 cells total, run
```python $MCTOOLS/mctools/mcnp/vol.py -card vol -ntotal 10 -values "5 3.14 7 2.71" -default j```.
		This generates the required data card: ```vol 4j 3.1 j 2.7 3j```.
* [mcnpview](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/mcnpview.sh): a wrapper around ``mcnp ip`` which allows to return to the selected geometry view in subsequent calls of the viewer. Find the detailed tutorial in the [wiki section](https://github.com/kbat/mc-tools/wiki/mcnpview).

## PHITS
* Emacs [syntax highlighting script](https://github.com/kbat/mc-tools/blob/master/mctools/phits/phits-mode.el) for [PHITS](http://phits.jaea.go.jp/).
* ANGEL to [ROOT](http://root.cern) converter (converts the PHITS output into ROOT). Most of the tallies are supported with PHITS 2, but it does not really work with PHITS 3.
* A script
    [rotate3dshow.py](https://github.com/kbat/mc-tools/blob/master/mctools/phits/rotate3dshow.py)
    which allows to animate the output of the **t-3dshow** tally. It
    runs PHITS to generate many images, so one can get a rotating
    video of geometry setup. Example:
    [snowman.gif](https://phits.jaea.go.jp/image/snowman.gif)
    (should be viewed with an image viewer which supports GIF
    animation).  A simplified version of this script with a detailed
    manual can be downloaded from the PHITS website:
    <http://phits.jaea.go.jp/examples.html>

## FLUKA
* Emacs [syntax highlighting script](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/fluka-mode.el) for [FLUKA](http://www.fluka.org).
* [fluka2root](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/fluka2root.py) tool to convert the FLUKA binary output into a [ROOT](https://root.cern) file. To understand how it works, run the standard example ```$FLUTIL/rfluka -N0 -M3 $FLUPRO/exmixed.inp``` and then execute ```fluka2root exmixed.inp```. It creates a single ROOT file out of all FLUKA-produced data files converted into the ROOT histograms or trees.
  * A more detailed tutorial is available in the [wiki section](https://github.com/kbat/mc-tools/wiki/FLUKA).
  * Internally, `fluka2root` uses the following convertes which can be called individually:
    * [usbsuw2root](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/usbsuw2root.py) script to convert the USRBIN results into a TH3F histogram. Note that this tool does not directly convert the files produced by the USRBIN card, but these files must first be averaged by the $FLUTIL/usbsuw program. The resulting averaged file can be converted into ROOT by usbsuw2root. The $FLUTIL/usbsuw call is done automatically if the [fluka2root](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/fluka2root.py) general converter is used.
    * [usxsuw2root](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/usxsuw2root.py) script to convert the USRBDX results into a TH2F histogram. + see the comments for the previous item.
    * [usrsuw2root](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/usrsuw2root.py) script to convertert the
RESNUCLEI results into a TH2F histogram and TGraphError + see the comments for ```usbsuw2root``` above. Known bug: isomer data is not saved into the ROOT file.
    * [ustsuw2root](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/ustsuw2root.py) script to convert the USRTRACK results into a TH1F histogram. + see the comments for ```usbsuw2root``` above.
    * [eventdat2root](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/eventdat2root.py) script to convert the EVENTDAT results into a TTree object.
* [plotgeom2root](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/plotgeom2root.py) script to convert the [PLOTGEOM](http://www.fluka.org/fluka.php?id=man_onl&sub=63) binary output into a [TMultiGraph](https://root.cern/root/html606/classTMultiGraph.html) object.

## Generic tools
* A Python module to calculate atomic fractions of isotopes in a
    mixture for the given volume fractions of materials. Some examples
    can be found in
    [mixtures.py](https://github.com/kbat/mc-tools/blob/master/mctools/common/mixtures.py).
* [ace2root](https://github.com/kbat/mc-tools/blob/master/mctools/common/ace2root.py), a converter from ACE (a compact ENDF) to ROOT formats. It loops through all available cross-sections in an ACE file and saves them as TGraph objects. We use this simple script to visualise [ENDF](http://www.nndc.bnl.gov/exfor/endf00.jsp) cross sections. Requires the [PyNE](http://pyne.io) toolkit to be installed.
* [hplot](https://github.com/kbat/mc-tools/tree/master/mctools/common/hplot), an advanced [TH3](https://root.cern.ch/doc/v608/classTH3.html) histogram plotter. We use it to visualise data maps and superimpose them with Monte Carlo geometry. A detailed manual can be generted with the ```-h``` argument.

## Requirements ##
* The ROOT-related scripts (file names end with ```*2root```), require [ROOT](http://root.cern) to be compiled with Python 3 support.
  * In order to check whether the Python
    support in ROOT is set up correctly, say
    ```import ROOT```
    in the Python 3 shell. You should not see any error messages.
* ```hplot``` requires the [Boost](https://www.boost.org) libraries and ROOT to be compiled with at least ```C++17``` standard.
* ```ace2root``` needs the [PyNE](http://pyne.io) toolkit.
* If the [GNU parallel](https://www.gnu.org/software/parallel) tool is
  installed then the FLUKA merge and ROOT converter tools called by
  the ```fluka2root``` script will use all available cores which makes
  them run faster.
* Linux and MacOS are supported. We have never tried to use these
  tools on Windows.

## Installation ##

1. Get the source code:
    - either
```git clone https://github.com/kbat/mc-tools.git```
    - or download and uncompress ```https://github.com/kbat/mc-tools/archive/master.zip```
2. Set the variable MCTOOLS to the folder where you have installed the
   code:
```export MCTOOLS=/path/to/mc-tools```
   (specify the folder containing README.md)
3. Add the ```$MCTOOLS``` folder into ```$PYTHONPATH```:
```export PYTHONPATH=$MCTOOLS:$PYTHONPATH```
4. Add the ```$MCTOOLS/bin``` folder into your ```$PATH```:
``` export PATH=$MCTOOLS/bin:$PATH ```

## Contacts ##
e-mail: `batkov [аt] gmail.com`

List of authors: Nicolò Borghi, Kazuyoshi Furutaka, Konstantin Batkov

## See also ##
https://github.com/lanl/mcnptools

https://github.com/SAnsell/CombLayer

http://pyne.io

https://github.com/Lindt8/DCHAIN-Tools
