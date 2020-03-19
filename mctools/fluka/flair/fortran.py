#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright European Organization for Nuclear Research (CERN)
# All rights reserved
#
# Author: Vasilis.Vlachoudis@cern.ch
# Date:   24-Oct-2006

__author__ = "Vasilis Vlachoudis"
__email__  = "Vasilis.Vlachoudis@cern.ch"

import struct

#-------------------------------------------------------------------------------
# Skip a fortran block from a binary file
# @param f file to read from
# @return size, None for EOF
#-------------------------------------------------------------------------------
def skip(f):
	blen = f.read(4)
	if not blen: return 0
	(size,) = struct.unpack("=i", blen)
	f.seek(size, 1)
	blen2 = f.read(4)
	if blen != blen2:
		raise IOError("Skipping fortran block")
	return size

#-------------------------------------------------------------------------------
# Read a fortran structure from a binary file
# @param f file to read from
# @return data, None for EOF
#-------------------------------------------------------------------------------
def read(f):
	blen = f.read(4)
	if not blen: return None
	(size,) = struct.unpack("=i", blen)
	data  = f.read(size)
	blen2 = f.read(4)
	if blen != blen2:
		raise IOError("Reading fortran block")
	return data

#-------------------------------------------------------------------------------
# Write a block of data (string) to file as a fortran block
# @param f	file to write to
# @param d	data to write
# @return output of last write statement
#-------------------------------------------------------------------------------
def write(f, d):
	f.write(struct.pack("=i",len(d)))
	f.write(d)
	return f.write(struct.pack("=i",len(d)))
