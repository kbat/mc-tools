#!/usr/bin/python -W all
#
# Adopted from $ROOTSYS/tutorials/pyroot/DynamicSlice.py

import sys

from ROOT import gRandom, gPad, gROOT, gVirtualX
from ROOT import kTRUE, kRed
from ROOT import TCanvas, TH2, TH2F, Double


class DynamicSlice:

   def __init__( self, hname, nbins ):
      self._cX   = None
      self._cY   = None
      self._old  = None
      self.hname = hname
      self.nbins = nbins

   def __call__( self ):

      h = self.hname
      if not h:
         return

      if not isinstance( h, TH2 ):
         return

      gPad.GetCanvas().FeedbackMode( kTRUE )

    # erase old position and draw a line at current position
      px = gPad.GetEventX()
      py = gPad.GetEventY()

      uxmin, uxmax = gPad.GetUxmin(), gPad.GetUxmax()
      uymin, uymax = gPad.GetUymin(), gPad.GetUymax()
      pxmin, pxmax = gPad.XtoAbsPixel( uxmin ), gPad.XtoAbsPixel( uxmax )
      pymin, pymax = gPad.YtoAbsPixel( uymin ), gPad.YtoAbsPixel( uymax )

      if self._old != None:
         gVirtualX.DrawLine( pxmin, self._old[1], pxmax, self._old[1] )
         gVirtualX.DrawLine( self._old[0], pymin, self._old[0], pymax )
      gVirtualX.DrawLine( pxmin, py, pxmax, py )
      gVirtualX.DrawLine( px, pymin, px, pymax )

      self._old = px, py

      upx = gPad.AbsPixeltoX( px )
      x = gPad.PadtoX( upx )
      upy = gPad.AbsPixeltoY( py )
      y = gPad.PadtoY( upy )

      padsav = gPad

    # create or set the display canvases
      if not self._cX:
         self._cX = gPad.GetCanvas().GetPad(2)
      else:
         self._DestroyPrimitive( 'X' )

      if not self._cY:
         self._cY = gPad.GetCanvas().GetPad(3)
      else:
         self._DestroyPrimitive( 'Y' )

      self.DrawSlice( h, y, 'Y' )
#      self.DrawSlice( h, x, 'X' )

      padsav.cd()

   def _DestroyPrimitive( self, xy ):
      proj = getattr( self, '_c'+xy ).GetPrimitive( 'Projection '+xy )
      if proj:
         proj.IsA().Destructor( proj )

   def DrawSlice( self, histo, value, xy ):
      yx = xy == 'X' and 'Y' or 'X'

    # draw slice corresponding to mouse position
      canvas = getattr( self, '_c'+xy )
      canvas.SetGrid()
      canvas.cd()

      bin = getattr( histo, 'Get%saxis' % xy )().FindBin( value )
      hp = getattr( histo, 'Projection' + yx )( '', bin, bin+self.nbins-1 )
      hp.SetFillColor( 38 )
      hp.SetName( 'Projection ' + xy )
      hp.SetTitle( xy + 'Projection of bin=%d' % bin )
      hp.Scale(1.0/self.nbins)
      hp.Smooth(self.nbins)
      hp.Draw("hist");
      hp.GetYaxis().SetMaxDigits(2)
      canvas.Update()
