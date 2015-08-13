# mc-tools
Some Monte Carlo tools.

 * MСNР(Х)
  * An implementation of application programming interface (API) to read tallies from *mctal* files into a [https://code.google.com/p/mc-tools/source/browse/trunk/mcnp/mctal.py Tally] object. This API allows to convert *mctal* files into any format.  It should work with any tallies except of the kcode data and tallies with perturbation records.
  * The [https://code.google.com/p/mc-tools/source/browse/trunk/mcnp/mctal2root.py mctal2root] script shows an example how to save a mctal file in the [http://root.cern.ch ROOT]  format.  [https://drive.google.com/file/d/0B35Xg1IpFgVycXRiWWh0VTJnczQ/edit?usp=sharing This poster] presented on the [http://j-parc.jp/researcher/MatLife/en/meetings/ICANS_XXI/ ICANS XXI] conference shows some usage examples.
  * WSSA file converters
   * [https://code.google.com/p/mc-tools/source/browse/trunk/mcnp/ssw2txt.py ssw2txt] converter: it converts WSSA files produced by MCNP(X) into plain text. The comments in the script explain how to derive additional information (like particle type and surface crossed) from the WSSA records.
   * [https://code.google.com/p/mc-tools/source/browse/trunk/mcnp/ssw2root.py ssw2root] converter: it converts WSSA files produced by MСNР(X) into a ROOT ntuple. Use TTree::GetAlias() to get particle type and surface crossed. The list of aliases defined in the tree can be printed by the TTree::GetListOfAliases()::Print() method. [https://code.google.com/p/mc-tools/source/browse/trunk/mcnp/examples/ssw2root/example.C This macro] shows several very simple examples how to analyse SSW files with ROOT. 
  The WSSA file format depends on the MCNPX version, and currently the script has been tested with versions 2.6.0, 26b, 2.7.0 and MCNP6. If you are experiencing problems with this script, you are welcome [https://code.google.com/u/batkov to contact the author].
  * A Python module to calculate atomic fractions of isotopes in a mixture for the given volume fractions of materials. Some examples can be found in  [http://code.google.com/p/mc-tools/source/browse/trunk/common/mixtures.py mixtures.py].
 * PHITS
  * Emacs syntax highlighting script for [http://phits.jaea.go.jp/ PHITS].
  * ANGEL to [http://root.cern.ch ROOT] converter (converts the PHITS output to ROOT) - most of the tallies are supported, but there are known bugs and limitations, should be used with care.
  * A script [http://code.google.com/p/mc-tools/source/browse/trunk/phits/rotate3dshow.py rotate3dshow.py] which allows to animate the output of the *t-3dshow* tally. It runs PHITS to generate many images, so one can get a rotating video of geometry setup. Example: [http://mc-tools.googlecode.com/files/rotate3dshow.gif rotate3dshow.gif] (should be viewed with an image viewer which supports GIF animation).  A simplified version of this script with a detailed manual can be downloaded from the PHITS website: http://phits.jaea.go.jp/examples.html
 * FLUKA
  * See the [http://code.google.com/p/readfluka readfluka] project.
 * Generic tools
  * A Python module to calculate atomic fractions of isotopes in a mixture for the given volume fractions of materials. Some examples can be found in  [http://code.google.com/p/mc-tools/source/browse/trunk/common/mixtures.py mixtures.py].

== Installation ==
 # Get the mc-tools source code:
{{{
svn checkout http://mc-tools.googlecode.com/svn/trunk/ mc-tools
}}}
 # Set the variable MCTOOLS to the folder where you have installed the code. For instance:
{{{
export MCTOOLS=/path/to/mc-tools
}}}
 # Update your PHYTHONPATH (add this line in ~/.bashrc in order to save this setting for your future sessions):
{{{
export PYTHONPATH=$MCTOOLS/phits:$MCTOOLS/mcnp:$PYTHONPATH
}}}
 # If you are going to use ROOT-related scripts (such as mctal2root, ssw2root or angel2root), you need to have [http://root.cern.ch ROOT] to be compiled with Python support. Follow [http://root.cern.ch/drupal/content/pyroot this manual] for more details. Otherwise you can skip this step. To check whether the Python support is set up correctly, say 
{{{
import ROOT
}}} 
 in the Python shell. You should not see any error messages.


=== Contacts ===
e-mail: `mc-tools [аt] lizardie.com`

=== See also ===
[http://pyne.io http://pyne.io]
