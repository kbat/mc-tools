/*********************************************************************
  CombLayer : MCNP(X) Input builder

 * File:   CXXDIR/MyComponent.cxx
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
#include <memory>

#include "FileReport.h"
#include "NameStack.h"
#include "RegMethod.h"
#include "OutputLog.h"
#include "BaseVisit.h"
#include "Vec3D.h"
#include "surfRegister.h"
#include "varList.h"
#include "Code.h"
#include "FuncDataBase.h"
#include "HeadRule.h"
#include "groupRange.h"
#include "objectGroups.h"
#include "Simulation.h"
#include "ModelSupport.h"
#include "MaterialSupport.h"
#include "generateSurf.h"
#include "LinkUnit.h"
#include "FixedComp.h"
#include "FixedRotate.h"
#include "ContainedComp.h"
#include "BaseMap.h"
#include "CellMap.h"
#include "SurfMap.h"

#include "MyComponent.h"

namespace NAMESPACE
{

MyComponent::MyComponent(const std::string& Key)  :
  attachSystem::ContainedComp(),
  attachSystem::FixedRotate(Key,6),
  attachSystem::CellMap(),
  attachSystem::SurfMap()
 /*!
    Constructor BUT ALL variable are left unpopulated.
    \param Key :: Name for item in search
  */
{}

MyComponent::MyComponent(const MyComponent& A) :
  attachSystem::ContainedComp(A),
  attachSystem::FixedRotate(A),
  attachSystem::CellMap(A),
  attachSystem::SurfMap(A),
  length(A.length),width(A.width),height(A.height),
  mainMat(A.mainMat)
  /*!
    Copy constructor
    \param A :: MyComponent to copy
  */
{}

MyComponent&
MyComponent::operator=(const MyComponent& A)
  /*!
    Assignment operator
    \param A :: MyComponent to copy
    \return *this
  */
{
  if (this!=&A)
    {
      attachSystem::ContainedComp::operator=(A);
      attachSystem::FixedRotate::operator=(A);
      attachSystem::CellMap::operator=(A);
      length=A.length;
      width=A.width;
      height=A.height;
      mainMat=A.mainMat;
    }
  return *this;
}

MyComponent*
MyComponent::clone() const
/*!
  Clone self
  \return new (this)
 */
{
    return new MyComponent(*this);
}

MyComponent::~MyComponent()
  /*!
    Destructor
  */
{}

void
MyComponent::populate(const FuncDataBase& Control)
  /*!
    Populate all the variables
    \param Control :: Variable data base
  */
{
  ELog::RegMethod RegA("MyComponent","populate");

  FixedRotate::populate(Control);

  length=Control.EvalVar<double>(keyName+"Length");
  width=Control.EvalVar<double>(keyName+"Width");
  height=Control.EvalVar<double>(keyName+"Height");

  mainMat=ModelSupport::EvalMat<int>(Control,keyName+"MainMat");

  return;
}

void
MyComponent::createSurfaces()
  /*!
    Create All the surfaces
  */
{
  ELog::RegMethod RegA("MyComponent","createSurfaces");

  SurfMap::makePlane("back",SMap,buildIndex+1,Origin-Y*(length/2.0),Y);
  SurfMap::makePlane("front",SMap,buildIndex+2,Origin+Y*(length/2.0),Y);

  SurfMap::makePlane("left",SMap,buildIndex+3,Origin-X*(width/2.0),X);
  SurfMap::makePlane("right",SMap,buildIndex+4,Origin+X*(width/2.0),X);

  SurfMap::makePlane("bottom",SMap,buildIndex+5,Origin-Z*(height/2.0),Z);
  SurfMap::makePlane("top",SMap,buildIndex+6,Origin+Z*(height/2.0),Z);

  return;
}

void
MyComponent::createObjects(Simulation& System)
  /*!
    Adds the all the components
    \param System :: Simulation to create objects in
  */
{
  ELog::RegMethod RegA("MyComponent","createObjects");

  HeadRule Out;
  Out=ModelSupport::getHeadRule(SMap,buildIndex," 1 -2 3 -4 5 -6 ");
  makeCell("MainCell",System,cellIndex++,mainMat,0.0,Out);

  addOuterSurf(Out);

  return;
}


void
MyComponent::createLinks()
  /*!
    Create all the linkes
  */
{
  ELog::RegMethod RegA("MyComponent","createLinks");

  FixedComp::setConnect(0,Origin-Y*(length/2.0),-Y);
  FixedComp::setNamedLinkSurf(0,"Back",SurfMap::getSignedSurf("#back"));

 TODO: Check and use names for the links below:

  FixedComp::setConnect(1,Origin+Y*(length/2.0),Y);
  FixedComp::setNamedLinkSurf(1,"Front",SMap.realSurf(buildIndex+2));

  FixedComp::setConnect(2,Origin-X*(width/2.0),-X);
  FixedComp::setNamedLinkSurf(2,"Left",-SMap.realSurf(buildIndex+3));

  FixedComp::setConnect(3,Origin+X*(width/2.0),X);
  FixedComp::setNamedLinkSurf(3,"Right",SMap.realSurf(buildIndex+4));

  FixedComp::setConnect(4,Origin-Z*(height/2.0),-Z);
  FixedComp::setNamedLinkSurf(4,"Bottom",-SMap.realSurf(buildIndex+5));

  FixedComp::setConnect(5,Origin+Z*(height/2.0),Z);
  FixedComp::setNamedLinkSurf(5,"Top",SMap.realSurf(buildIndex+6));

  return;
}

void
MyComponent::createAll(Simulation& System,
		       const attachSystem::FixedComp& FC,
		       const long int sideIndex)
  /*!
    Generic function to create everything
    \param System :: Simulation item
    \param FC :: Central origin
    \param sideIndex :: link point for origin
  */
{
  ELog::RegMethod RegA("MyComponent","createAll");

  populate(System.getDataBase());
  createUnitVector(FC,sideIndex);
  createSurfaces();
  createObjects(System);
  createLinks();
  insertObjects(System);

  return;
}

}  // NAMESPACE
