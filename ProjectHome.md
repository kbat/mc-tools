Some Monte Carlo tools.

  * MСNР(Х)
    * An implementation of application programming interface (API) to read tallies from **mctal** files into a [Tally](https://code.google.com/p/mc-tools/source/browse/trunk/mcnp/mctal.py) object. This API allows to convert **mctal** files into any format.  It should work with any tallies except of the kcode data and tallies with perturbation records.
    * The [mctal2root](https://code.google.com/p/mc-tools/source/browse/trunk/mcnp/mctal2root.py) script shows an example how to save a mctal file in the [ROOT](http://root.cern.ch)  format.  [This poster](https://drive.google.com/file/d/0B35Xg1IpFgVycXRiWWh0VTJnczQ/edit?usp=sharing) presented on the [ICANS XXI](http://j-parc.jp/researcher/MatLife/en/meetings/ICANS_XXI/) conference shows some usage examples.
    * WSSA file converters
      * [ssw2txt](https://code.google.com/p/mc-tools/source/browse/trunk/mcnp/ssw2txt.py) converter: it converts WSSA files produced by MCNP(X) into plain text. The comments in the script explain how to derive additional information (like particle type and surface crossed) from the WSSA records.
      * [ssw2root](https://code.google.com/p/mc-tools/source/browse/trunk/mcnp/ssw2root.py) converter: it converts WSSA files produced by MСNР(X) into a ROOT ntuple. Use TTree::GetAlias() to get particle type and surface crossed. The list of aliases defined in the tree can be printed by the TTree::GetListOfAliases()::Print() method. [This macro](https://code.google.com/p/mc-tools/source/browse/trunk/mcnp/examples/ssw2root/example.C) shows several very simple examples how to analyse SSW files with ROOT.
> > The WSSA file format depends on the MCNPX version, and currently the script has been tested with versions 2.6.0, 26b, 2.7.0 and MCNP6. If you are experiencing problems with this script, you are welcome [to contact the author](https://code.google.com/u/batkov).
    * A Python module to calculate atomic fractions of isotopes in a mixture for the given volume fractions of materials. Some examples can be found in  [mixtures.py](http://code.google.com/p/mc-tools/source/browse/trunk/common/mixtures.py).
  * PHITS
    * Emacs syntax highlighting script for [PHITS](http://phits.jaea.go.jp/).
    * ANGEL to [ROOT](http://root.cern.ch) converter (converts the PHITS output to ROOT) - most of the tallies are supported, but there are known bugs and limitations, should be used with care.
    * A script [rotate3dshow.py](http://code.google.com/p/mc-tools/source/browse/trunk/phits/rotate3dshow.py) which allows to animate the output of the **t-3dshow** tally. It runs PHITS to generate many images, so one can get a rotating video of geometry setup. Example: [rotate3dshow.gif](http://mc-tools.googlecode.com/files/rotate3dshow.gif) (should be viewed with an image viewer which supports GIF animation).  A simplified version of this script with a detailed manual can be downloaded from the PHITS website: http://phits.jaea.go.jp/examples.html
  * FLUKA
    * See the [readfluka](http://code.google.com/p/readfluka) project.
  * Generic tools
    * A Python module to calculate atomic fractions of isotopes in a mixture for the given volume fractions of materials. Some examples can be found in  [mixtures.py](http://code.google.com/p/mc-tools/source/browse/trunk/common/mixtures.py).

## Installation ##
  1. Get the mc-tools source code:
```
svn checkout http://mc-tools.googlecode.com/svn/trunk/ mc-tools
```
  1. Set the variable MCTOOLS to the folder where you have installed the code. For instance:
```
export MCTOOLS=/path/to/mc-tools
```
  1. Update your PHYTHONPATH (add this line in ~/.bashrc in order to save this setting for your future sessions):
```
export PYTHONPATH=$MCTOOLS/phits:$MCTOOLS/mcnp:$PYTHONPATH
```
  1. If you are going to use ROOT-related scripts (such as mctal2root, ssw2root or angel2root), you need to have [ROOT](http://root.cern.ch) to be compiled with Python support. Follow [this manual](http://root.cern.ch/drupal/content/pyroot) for more details. Otherwise you can skip this step. To check whether the Python support is set up correctly, say
```
import ROOT
```

> in the Python shell. You should not see any error messages.


### Contacts ###
e-mail: `mc-tools [аt] lizardie.com`

### See also ###
[http://pyne.io](http://pyne.io)