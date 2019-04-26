#! /usr/bin/python -W all
# Generates xbindkeys configuration file for MCNP viewer

from __future__ import print_function
import sys

class XDoTool:
    def __init__(self, title):
        print("# ", title)
        print('"xdotool ', end='')

    def MouseMove(self, x, y):
        print(" mousemove %d %d" % (x, y), end='')

    def MouseMove1(self, coord):
        return self.MouseMove(coord[0], coord[1])

    def Click(self, button, repeat=1):
        if repeat==1:
            print(" click %d" % button, end='')
        else:
            print(" click --repeat %d %d" % (repeat, button), end='')

    def SetKey(self, title, key):
        print('"')
        print(" "*3, key)
        print("# ", title)
        print("")

    def Restore(self):
        print(" restore", end='')

    def Redraw(self):
        self.MouseMove(100,100)
        self.Click(1)

def main():
    COLOR = [25, 650]

    # screen resolution
    dx = 1920
    dy = 1200
    
    update = XDoTool("update (draw) mcplot")
    update.Redraw()
    update.SetKey("Control+Mod4 + r", "control+alt+r")

    q = XDoTool("exit mcplot")
    q.MouseMove(0.86*dx,0.96*dy)
    q.Click(1)
    q.SetKey("Control+Mod4 + q",  "control+alt+q")

    y = 0.06*dy

    unzoom2 = XDoTool("zoom x.2")
    unzoom2.MouseMove(0.703*dx, y)
    unzoom2.Click(1, 2)
    unzoom2.Restore()
    unzoom2.SetKey("Control+Mod4 + minus", "control+alt+minus")

    zoom5 = XDoTool("zoom x5")
    zoom5.MouseMove(0.833*dx, y)
    zoom5.Click(1, 2)
    zoom5.Restore()
    zoom5.SetKey("Control+Mod4 + equal", "control+alt+equal")

    y = 0.775*dy

    xy = XDoTool("show xy projection")
    xy.MouseMove(0.052*dx, y)
    xy.Click(1)
    xy.SetKey("Control+Mod4 + x", "control+alt+x")

    yz = XDoTool("show yz projection")
    yz.MouseMove(0.104*dx, y)
    yz.Click(1)
    yz.SetKey("Control+Mod4 + y", "control+alt+y")

    zx = XDoTool("show zx projection")
    zx.MouseMove(0.208*dx, y)
    zx.Click(1)
    zx.SetKey("Control+Mod4 + z", "control+alt+z")

    up  = XDoTool("shift a bit up")
    up.MouseMove(782, 42)
    up.Click(1)
    up.MouseMove(900, 500)
    up.Click(1)
    up.Restore()
    up.SetKey("Control+Mod4 + Down", "m:0x44 + c:116")

    down  = XDoTool("shift a bit down")
    down.MouseMove(782, 42)
    down.Click(1)
    down.MouseMove(900, 400)
    down.Click(1)
    down.Restore()
    down.SetKey("Control+Mod4 + Up", "m:0x44 + c:111")

    left  = XDoTool("shift a bit left")
    left.MouseMove(782, 42)
    left.Click(1)
    left.MouseMove(850, 450)
    left.Click(1)
    left.Restore()
    left.SetKey("Control+Mod4 + Left", "m:0x44 + c:113")

    right  = XDoTool("shift a bit right")
    right.MouseMove(782, 42)
    right.Click(1)
    right.MouseMove(950, 450)
    right.Click(1)
    right.Restore()
    right.SetKey("Control+Mod4 + Right", "m:0x44 + c:114")

    T  = XDoTool("color temperature")
    T.MouseMove(1400, 370)
    T.Click(1)
    T.MouseMove1(COLOR)
    T.Click(1, 2)
    T.Redraw()
    T.Restore()
    T.SetKey("Control+Mod4 + t", "m:0x44 + c:28")
    
    M  = XDoTool("color material")
    M.MouseMove(1400, 335)
    M.Click(1)
    M.MouseMove1(COLOR)
    M.Click(1, 2)
    M.Redraw()
    M.SetKey("Control+Mod4 + m", "m:0x44 + c:58")
    
    rotate = XDoTool("rotate")
    rotate.MouseMove(0.104*dx, 0.708*dy)
    rotate.Click(1)
    M.Redraw()
    rotate.SetKey("Control + Mod4 + e", "control+alt+e")

    scales = XDoTool("scales")
    scales.MouseMove(200, 650)
    scales.Click(1)
    M.Redraw()
    scales.SetKey("Control + Mod4 + s", "m:0x44 + c:39")

if __name__ == "__main__":
    sys.exit(main())
