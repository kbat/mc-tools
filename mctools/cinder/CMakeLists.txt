cmake_minimum_required(VERSION 2.6 FATAL_ERROR)
project(alltabs)

set(CMAKE_CXX_COMPILER clang)
set(CMAKE_CXX_FLAGS "-fPIC -Wconversion -W -Wall -Wextra -Wno-comment -fexceptions -std=c++1y -Wno-unused-parameter")
set(CMAKE_CXX_RELEASE_FLAGS "-fPIC -Wconversion -W -Wall -Wextra -Wno-comment -fexceptions -std=c++1y -O2 ")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ./lib)
set(CMAKE_INSTALL_LIBDIR $ENV{ROOTSYS}/lib)

if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
set(CMAKE_SHARED_LIBRARY_CREATE_CXX_FLAGS "${CMAKE_SHARED_LIBRARY_CREATE_CXX_FLAGS} -undefined dynamic_lookup")
endif()

list(APPEND CMAKE_PREFIX_PATH $ENV{ROOTSYS})
find_package(ROOT REQUIRED)
include(${ROOT_USE_FILE})

include_directories(${CMAKE_CURRENT_SOURCE_DIR})
include_directories(${CMAKE_CURRENT_BINARY_DIR})

include_directories(${ROOT_INCLUDE_DIR})

include_directories(${PROJECT_SOURCE_DIR}/include)

file(GLOB ALLTABS_SOURCES ${PROJECT_SOURCE_DIR}/src/*.cxx)
file(GLOB ALLTABS_HEADERS ${PROJECT_SOURCE_DIR}/include/*.h)

ROOT_GENERATE_DICTIONARY(libAlltabsDict include/TNuclide.h include/TTable.h
                          LINKDEF include/LinkDef.h
                          OPTIONS -rmf libAlltabs.rootmap
                                  -rml libAlltabs
                                  -s libAlltabs)


add_library(Alltabs SHARED src/TNuclide.cxx src/TTable.cxx libAlltabsDict.cxx)
target_link_libraries(Alltabs ${ROOT_LIBRARIES})

add_executable(alltabs2ttree ${ALLTABS_SOURCES} ${ALLTABS_HEADERS})

target_link_libraries(alltabs2ttree ${ROOT_LIBRARIES})
