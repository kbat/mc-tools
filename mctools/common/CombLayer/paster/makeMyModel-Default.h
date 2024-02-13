/*********************************************************************
  CombLayer : MCNP(X) Input builder

 * File:   INCDIR/MyModel.h
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
#ifndef NAMESPACE_makeMODEL_h
#define NAMESPACE_makeMODEL_h

namespace NAMESPACE
{
  /*!
    \class makeMODEL
    \version 1.0
    \author AUTHOR
    \date DATE
    \brief DESCRIPTION
  */

class makeMODEL
{
 private:

 public:

  makeMODEL();
  makeMODEL(const makeMODEL&);
  makeMODEL& operator=(const makeMODEL&);
  ~makeMODEL();

  void build(Simulation&,const mainSystem::inputParam&);

};

}

#endif
