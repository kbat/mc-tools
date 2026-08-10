#ifndef Palette_h_
#define Palette_h_

#include <string>

/*!
  Set the colour map scheme.

  Accepts "MAXIV" (the built-in gradient exported from ParaView) or any of the
  palette names predefined in TColor::EColorPalette, e.g. "kDeepSea".  A name
  preceded by a minus sign, e.g. "-kDeepSea", selects the inverted palette.

  Returns false (and leaves the current palette alone) if the name is unknown.
*/
bool SetColourMap(const std::string& palette = "MAXIV");

#endif
