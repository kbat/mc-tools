/*********************************************************************
  CombLayer : MCNP(X) Input builder

 * File:   INCDIR/MyComponent.h
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
#ifndef NAMESPACE_MyComponent_h
#define NAMESPACE_MyComponent_h

class Simulation;

namespace NAMESPACE
{

/*!
  \class MyComponent
  \version 1.0
  \author AUTHOR
  \date DATE
  \brief DESCRIPTION
*/

class MyComponent : public attachSystem::ContainedComp,
                    public attachSystem::FixedRotate,
                    public attachSystem::CellMap,
                    public attachSystem::SurfMap
{
 private:

  double length;                ///< Total length including void
  double width;                 ///< Width
  double height;                ///< Height

  int mainMat;                   ///< Main material

  void populate(const FuncDataBase&);
  void createSurfaces();
  void createObjects(Simulation&);
  void createLinks();

 public:

  MyComponent(const std::string&);
  MyComponent(const MyComponent&);
  MyComponent& operator=(const MyComponent&);
  virtual MyComponent* clone() const;
  virtual ~MyComponent();

  using attachSystem::FixedComp::createAll;
  void createAll(Simulation&,const attachSystem::FixedComp&,const long int);

};

}

#endif
