#
# Copyright European Organization for Nuclear Research (CERN)
# All rights reserved
#
# Author: Vasilis.Vlachoudis@cern.ch
# Date:   10-Oct-2014

__author__ = "Vasilis Vlachoudis"
__email__  = "Vasilis.Vlachoudis@cern.ch"

#-------------------------------------------------------------------------------
# FIXME convert to class with static members
#-------------------------------------------------------------------------------
_outunit = None		# log unit
_repeat  = set()	# avoid repeated errors
_buffer  = None		# buffered output

#-------------------------------------------------------------------------------
def _output(txt, repeat=True):
	global _outunit
	if not repeat and txt in _repeat: return
	if _outunit is not None:
		_outunit(txt)
	else:
		if _buffer is not None:
			_buffer.append(txt)
		print(txt)

#-------------------------------------------------------------------------------
# Print out something in the log unit
#-------------------------------------------------------------------------------
def say(*args):
	"""say/print a message"""
	_output(" ".join(map(str,args)))
