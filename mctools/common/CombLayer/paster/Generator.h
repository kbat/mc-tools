/*********************************************************************
  CombLayer : MCNP(X) Input builder

 * File:   INCDIR/MyComponentGenerator.h
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
#ifndef setVariable_MyComponentGenerator_h
#define setVariable_MyComponentGenerator_h

class FuncDataBase;

namespace setVariable
{

/*!
  \class MyComponentGenerator
  \version 1.0
  \author AUTHOR
  \date DATE
  \brief MyComponentGenerator for variables
*/

class MyComponentGenerator
{
 private:

  double length;                ///< Total length including void
  double width;                 ///< Width
  double height;                ///< Height
  double wallThick;             ///< Wall thickness

  int mainMat;                  ///< Main material
  int wallMat;                  ///< Wall material

 public:

  MyComponentGenerator();
  MyComponentGenerator(const MyComponentGenerator&);
  MyComponentGenerator& operator=(const MyComponentGenerator&);
  virtual ~MyComponentGenerator();

  virtual void generate(FuncDataBase&,const std::string&) const;

};

}

#endif
