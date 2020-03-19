#!/usr/bin/env python3

import sys, argparse

class XDoTool:
    xoffset = 0
    yoffset = 0

    def __init__(self, title):
        print("# ", title)
        print('"xdotool ', end='')

    def MouseMove(self, x, y):
        print(" mousemove %d %d" % (x+self.xoffset, y+self.yoffset), end='')

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
    """ Generates xbindkeys configuration file for MCNP viewer
    The key names can be obtained with the 'xev' tool from x11-utils
    """
    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('-dx', type=int, default=1920, dest='dx', help='X screen resolution')
    parser.add_argument('-dy', type=int, default=1200, dest='dy', help='Y screen resolution')
    parser.add_argument('-xoffset', type=int, default=2560, dest='xoffset', help='Absolute X offset (e.g. due to 2nd monitor)')
    parser.add_argument('-yoffset', type=int, default=0, dest='yoffset', help='Absolute Y offset (e.g. due to 2nd monitor)')
    parser.add_argument('-mcnp', type=int, default=6, dest='mcnp', help='MCNP version. Either 6 or 10 (10 stands for X)', choices=(6,10))
    args = parser.parse_args()

    XDoTool.xoffset = args.xoffset
    XDoTool.yoffset = args.yoffset

    print("# ",sys.argv)

    if args.mcnp == 6:
        COLOR = [25, 650] # dummy
        right_menu_x = 0.9*args.dx # dummy
    else:
        COLOR = [0.06*args.dx, 0.78*args.dy]
        right_menu_x = 0.98*args.dx

    update = XDoTool("update (draw) mcplot")
    update.Redraw()
    update.SetKey("Control+Mod4 + r", "control+alt+r")

    q = XDoTool("exit mcplot")
    q.MouseMove(0.86*args.dx,0.96*args.dy)
    q.Click(1)
    q.SetKey("Control+Mod4 + q",  "control+alt+q")

    y = 0.06*args.dy

    unzoom2 = XDoTool("zoom x.2")
    unzoom2.MouseMove(0.703*args.dx, y)
    unzoom2.Click(1, 2)
    unzoom2.Restore()
    unzoom2.SetKey("Control+Mod4 + minus", "control+alt+minus")

    zoom5 = XDoTool("zoom x5")
    zoom5.MouseMove(0.833*args.dx, y)
    zoom5.Click(1, 2)
    zoom5.Restore()
    zoom5.SetKey("Control+Mod4 + equal", "control+alt+equal")

    if args.mcnp == 6:
        y = 0.775*args.dy
    else:
        y = 0.8 * args.dy

    xy = XDoTool("show xy projection")
    xy.MouseMove(0.052*args.dx, y)
    xy.Click(1)
    xy.SetKey("Control+Mod4 + x", "control+alt+x")

    yz = XDoTool("show yz projection")
    yz.MouseMove(0.104*args.dx, y)
    yz.Click(1)
    yz.SetKey("Control+Mod4 + y", "control+alt+y")

    zx = XDoTool("show zx projection")
    zx.MouseMove(0.211*args.dx, y)
    zx.Click(1)
    zx.SetKey("Control+Mod4 + z", "control+alt+z")

    origin = (0.573*args.dx, 0.06*args.dy)
    if args.mcnp == 6:
        center = (0.625*args.dx, 0.5*args.dy)
    else:
        center = (0.625*args.dx, 0.509*args.dy)

    up  = XDoTool("shift a bit up")
    up.MouseMove1(origin)
    up.Click(1)
    up.MouseMove(center[0], center[1]+50)
    up.Click(1)
    up.Restore()
    up.SetKey("Control+Mod4 + Down", "control+alt+Down")

    down  = XDoTool("shift a bit down")
    down.MouseMove1(origin)
    down.Click(1)
    down.MouseMove(center[0], center[1]-50)
    down.Click(1)
    down.Restore()
    down.SetKey("Control+Mod4 + Up", "control+alt+Up")

    left  = XDoTool("shift a bit left")
    left.MouseMove1(origin)
    left.Click(1)
    left.MouseMove(center[0]-50, center[1])
    left.Click(1)
    left.Restore()
    left.SetKey("Control+Mod4 + Left", "control+alt+Left")

    right  = XDoTool("shift a bit right")
    right.MouseMove1(origin)
    right.Click(1)
    right.MouseMove(center[0]+50, center[1])
    right.Click(1)
    right.Restore()
    right.SetKey("Control+Mod4 + Right", "control+alt+Right")

    if args.mcnp == 6:
        y = 0.708*args.dy
    else:
        y = 0.415*args.dy

    T  = XDoTool("color temperature")
    T.MouseMove(right_menu_x, y)
    T.Click(1)
    T.MouseMove1(COLOR)
    T.Click(1, 2)
    T.Redraw()
    T.Restore()
    T.SetKey("Control+Mod4 + t", "control+alt+t")
    
    if args.mcnp == 6:
        y = 0.708*args.dy # dummy
    else:
        y = 0.38*args.dy

    M  = XDoTool("color material")
    M.MouseMove(right_menu_x, y)
    M.Click(1)
    M.MouseMove1(COLOR)
    M.Click(1, 2)
    M.Redraw()
    M.SetKey("Control+Mod4 + m", "control+alt+m")
    
    if args.mcnp == 6:
        y = 0.708*args.dy
    else:
        y = 0.73 * args.dy

    rotate = XDoTool("rotate")
    rotate.MouseMove(0.104*args.dx, y)
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
