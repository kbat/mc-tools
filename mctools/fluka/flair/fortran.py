#!/bin/env python
# -*- coding: latin1 -*-
#
# Copyright and User License
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Copyright Vasilis.Vlachoudis@cern.ch for the
# European Organization for Nuclear Research (CERN)
#
# Please consult the flair documentation for the license
#
# DISCLAIMER
# ~~~~~~~~~~
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT
# NOT LIMITED TO, IMPLIED WARRANTIES OF MERCHANTABILITY, OF
# SATISFACTORY QUALITY, AND FITNESS FOR A PARTICULAR PURPOSE
# OR USE ARE DISCLAIMED. THE COPYRIGHT HOLDERS AND THE
# AUTHORS MAKE NO REPRESENTATION THAT THE SOFTWARE AND
# MODIFICATIONS THEREOF, WILL NOT INFRINGE ANY PATENT,
# COPYRIGHT, TRADE SECRET OR OTHER PROPRIETARY RIGHT.
#
# LIMITATION OF LIABILITY
# ~~~~~~~~~~~~~~~~~~~~~~~
# THE COPYRIGHT HOLDERS AND THE AUTHORS SHALL HAVE NO
# LIABILITY FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL,
# CONSEQUENTIAL, EXEMPLARY, OR PUNITIVE DAMAGES OF ANY
# CHARACTER INCLUDING, WITHOUT LIMITATION, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES, LOSS OF USE, DATA OR PROFITS,
# OR BUSINESS INTERRUPTION, HOWEVER CAUSED AND ON ANY THEORY
# OF CONTRACT, WARRANTY, TORT (INCLUDING NEGLIGENCE), PRODUCT
# LIABILITY OR OTHERWISE, ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGES.
#
# Author:	Vasilis.Vlachoudis@cern.ch
# Date:	24-Oct-2006

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
	if len(blen)==0: return 0
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
	if len(blen)==0: return None
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
