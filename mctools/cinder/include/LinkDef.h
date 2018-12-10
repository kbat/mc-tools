#ifdef __CLING__ /* Compiling with ROOT6 */
#pragma link off all globals;
#pragma link off all classes;
#pragma link off all functions;
#pragma link C++ nestedclasses;

#pragma link C++ class TTable+;
#pragma link C++ class TNuclide+;

#elif __CINT__ /* Compiling with ROOT5 */
#pragma link off all globals;
#pragma link off all classes;
#pragma link off all functions;
#pragma link C++ nestedclasses;

#pragma link C++ class TTable+;
#pragma link C++ class TNuclide+;

#endif

