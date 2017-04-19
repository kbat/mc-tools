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
  * The [mctal2root](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/mctal2root.py)
    script shows an example how to save a mctal file in the
    [ROOT](http://root.cern.ch)  format.
    [This poster](https://drive.google.com/file/d/0B35Xg1IpFgVycXRiWWh0VTJnczQ/edit?usp=sharing)
    presented on the
    [ICANS XXI](http://j-parc.jp/researcher/MatLife/en/meetings/ICANS_XXI/)
    conference shows some usage examples. 
  * WSSA file converters **(MCNP6 is not fully supported)**
    * [ssw2txt](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/ssw2txt.py)
      converter: it converts WSSA files produced by MCNP(X) into plain
      text. The comments in the script explain how to derive additional
      information (like particle type and surface crossed) from the
      WSSA records.
    * [ssw2root](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/ssw2root.py)
      converter: it converts WSSA files produced by MСNР(X) into a ROOT
      ntuple.  Use TTree::GetAlias() to get particle type and surface
      crossed.  The list of aliases defined in the tree can be printed
      by the TTree::GetListOfAliases()::Print()
      method.
      [This macro](https://github.com/kbat/mc-tools/blob/master/mctools/mcnp/examples/ssw2root/example.C)
      shows several very simple examples how to analyse SSW files with
      ROOT.  
    The WSSA file format depends on the MCNPX version, and currently
    the script has been tested with versions 2.6.0, 26b, 2.7.0 and
    MCNP6. If you are experiencing problems with this script, you are
    welcome [to contact the author](https://github.com/kbat). 
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
  * [usbsuw2root](https://github.com/kbat/mc-tools/blob/master/mctools/fluka/usbsuw2root.py) converter: it converts the USRBIN results into a TH3F histogram. Note that this tool does not directly convert the files produced by the USRBIN card, but these files must be processed by the $FLUTIL/usbsuw program which averages results and calculates statistical errors. The resulting file can be converted into ROOT by usbsuw2root. The $FLUTIL/usbsuw call must be done automatically if the fluka2root converter is used (see the [readfluka](https://github.com/kbat/readfluka) project).
  * More FLUKA-related tools are available in the [readfluka](https://github.com/kbat/readfluka) project. Unfortunatelly most of these tools are of low quality, but sometimes they work.
* Generic tools
  * A Python module to calculate atomic fractions of isotopes in a
    mixture for the given volume fractions of materials. Some examples
    can be found in
    [mixtures.py](https://github.com/kbat/mc-tools/blob/master/mctools/common/mixtures.py). 
   * [ace2root](https://github.com/kbat/mc-tools/blob/master/mctools/common/ace2root.py), a converter from ACE to ROOT formats. Loops through all available cross-sections in an ACE file and saves them as TGraph objects. We use this simple script to visualise [ENDF](http://www.nndc.bnl.gov/exfor/endf00.jsp) cross sections. Requires the [PyNE](http://pyne.io) toolkit to be installed.

## Requirements ##
* Python. Versions >= 3 are not supported (with exception of the ```rotate3dshow.py``` script).
* If you are going to use the ROOT-related scripts (such as mctal2root,
   ssw2root or angel2root), you need to have [ROOT](http://root.cern.ch)
   to be compiled with Python support. Follow
   [this manual](http://root.cern.ch/drupal/content/pyroot) for more
   details. To check whether the Python
   support is set up correctly, say   
   ```import ROOT```  
   in the Python shell. You should not see any error messages.
* If you are going to use the ```ace2root``` converter, you need to have [PyNE](http://pyne.io) toolkit to be installed.
* The FLUKA-related tools depend on [flair](http://www.fluka.org/flair) and assume it is installed in the `/usr/local/flair` folder. If your flair is installed in a different location, add it (as well as the `lib` subfolder) into $PYTHONPATH.

## Installation ##
Linux and MacOS are supported. However, we never tried yet to use these tools on Windows.

### System-wide installation ###
In order to use [pip](https://pip.pypa.io/en/stable/), you need to have the **python-setuptools** and **python-pip** modules installed on your system.

```pip install git+https://github.com/kbat/mc-tools.git```

You have to be either root or use ```--target``` argument to specify the folder. Read ```man pip``` for details.

Uninstall: ```pip uninstall mc-tools```.

### Developer and per-user installation ###

1. Get the source code:  
```git clone https://github.com/kbat/mc-tools.git```

   Now you need to adjust the $PYTHONPATH and $PATH variables for your system. You can do it as you like. The following steps describe an example how to do it.
2. Set the variable MCTOOLS to the folder where you have installed the
   code. For instance:   
```export MCTOOLS=/path/to/mc-tools/mctools```
3. Update your PHYTHONPATH (add this line in ~/.bashrc in order to
   save this setting for your future sessions):   
```export PYTHONPATH=$MCTOOLS:$PYTHONPATH```
4. Add the folders with necessary scripts in your $PATH or create symblinks to these scrips:
```export PATH=$MCTOOLS/mcnp:$PATH``` or
```ln -s $MCTOOLS/mcnp/mctal2root.py ~/bin/mctal2root```


### Contacts ###
e-mail: `batkov [аt] gmail.com`

List of authors: Nicolò Borghi, Kazuyoshi Furutaka, Konstantin Batkov

### See also ###
http://pyne.io

https://github.com/SAnsell/CombLayer
