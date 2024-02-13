/*********************************************************************
  CombLayer : MCNP(X) Input builder

 * File:   CXXDIR/makeMODEL.cxx
 *
 * Copyright (c) 2004-YEAR by AUTHOR
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 ****************************************************************************/
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <cmath>
#include <complex>
#include <list>
#include <vector>
#include <set>
#include <map>
#include <string>
#include <algorithm>
#include <iterator>
#include <memory>

#include "Exception.h"
#include "FileReport.h"
#include "NameStack.h"
#include "RegMethod.h"
#include "OutputLog.h"
#include "MatrixBase.h"
#include "inputParam.h"
#include "objectRegister.h"
#include "World.h"

#include "makeMODEL.h"

namespace NAMESPACE
{

makeMODEL::makeMODEL()
  /*!
    Constructor
  */
{}

makeMODEL::~makeMODEL()
  /*!
    Destructor
   */
{}

void
makeMODEL::build(Simulation& System,
		   const mainSystem::inputParam& IParam)
/*!
  Carry out the full build
  \param System :: Simulation system
  \param :: Input parameters
*/
{
  // For output stream
  ELog::RegMethod RControl("makeMODEL","build");



  return;
}


}
