#!/usr/bin/env python3
#
# Adopted from $ROOTSYS/tutorials/pyroot/DynamicSlice.py

from ROOT import gPad, gVirtualX
from ROOT import kTRUE, kSolid
from ROOT import TCanvas, TH2


class DynamicSlice:

   def __init__( self, hname, nbins):
      self._cX   = None
      self._cY   = None
      self._old  = None
      self.hname = hname
      self.nbins = nbins[0]
      self.ngroup = nbins[1]
      self.projection = 1
      self.logy = 0

   def __call__( self ):

      h = self.hname
      if not h:
         return

      if not isinstance( h, TH2 ):
         return

      gPad.GetCanvas().FeedbackMode( kTRUE )

      event = gPad.GetEvent()
      if (event==1): # left mouse click
         self.projection = not self.projection
      elif (event==12): # middle mouse click
         self.logy = not self.logy

    # erase old position and draw a line at current position
    #(gPad coordinate system)
      px = gPad.GetEventX()
      py = gPad.GetEventY()

      uxmin, uxmax = gPad.GetUxmin(), gPad.GetUxmax()
      uymin, uymax = gPad.GetUymin(), gPad.GetUymax()
      pxmin, pxmax = gPad.XtoAbsPixel( uxmin ), gPad.XtoAbsPixel( uxmax )
      pymin, pymax = gPad.YtoAbsPixel( uymin ), gPad.YtoAbsPixel( uymax )

      # if self.projection:
      #    axis = h.GetYaxis()
      # else:
      #    axis = h.GetXaxis()

      width = 1

      if self._old != None:
         if self.projection:
            gVirtualX.DrawBox( pxmin, self._old[1]-width, pxmax, self._old[1], kSolid)
         else:
            gVirtualX.DrawBox( self._old[0], pymin, self._old[0]+width, pymax, kSolid )
      if self.projection:
         gVirtualX.DrawBox( pxmin, py, pxmax, py+width, kSolid )
      else:
         gVirtualX.DrawBox( px, pymin, px, pymax+width, kSolid )

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
         self._cY = gPad.GetCanvas().GetPad(2)
      else:
         self._DestroyPrimitive( 'Y' )

      if self.projection:
         self.DrawSlice( h, y, 'Y' )
      else:
         self.DrawSlice( h, x, 'X' )

      padsav.cd()

   def _DestroyPrimitive( self, xy ):
      proj = getattr( self, '_c'+xy ).GetPrimitive( 'Projection '+xy )
      if proj:
         proj.IsA().Destructor( proj )

   def DrawSlice( self, histo, value, xy ):
      yx = xy == 'X' and 'Y' or 'X'
      vert_axis = xy == 'X' and 'Y' or 'X'

    # draw slice corresponding to mouse position
      canvas = getattr( self, '_c'+xy )
      canvas.SetGrid()
      canvas.cd()

      axis = getattr( histo, 'Get%saxis' % xy )()
      bin1 = axis.FindBin( value )
      bin2 = bin1+self.nbins-1
      vmin = axis.GetBinLowEdge(bin1)
      vmax = axis.GetBinLowEdge(bin2+1)
      hp = getattr( histo, 'Projection' + yx )( 'Projection ' + xy, bin1, bin2 )
      hp.SetFillColor( 38 )

      hp.SetTitle( xy + 'Projection of %d %s bins: %g < %s < %g (#Delta %s = %g)' % (self.nbins, vert_axis, vmin, vert_axis, vmax, vert_axis, vmax-vmin) )

      if self.ngroup >= 1:
         hp.Rebin(self.ngroup)

      if self.nbins > 1 or self.ngroup >=1:
         hp.Scale(1.0/(self.nbins*self.ngroup))

      hp.Draw("hist");
      yaxis = hp.GetYaxis()
      yaxis.SetMaxDigits(3)
      yaxis.SetTitle(histo.GetZaxis().GetTitle())
      canvas.SetLogy(self.logy)
      canvas.Update()
