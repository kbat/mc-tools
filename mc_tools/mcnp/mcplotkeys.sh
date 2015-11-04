#! /bin/bash
# -*- shell-script -*-
# xbindkeys config file generator for mcplot
# add its output in your ~/.xbindkeys
# 802 384 is the mcnpx screen center

# get screen dimensions
W=$(xrandr 2>/dev/null| grep '*'| cut -d x -f 1 | sed "s/ //g")
H=$(xrandr 2>/dev/null| grep '*'| cut -d x -f 2 | cut -d " " -f 1 | sed "s/ //g")

echo """
### mcplotkeys start ###
# update (draw) mcplot
\"xdotool mousemove $(echo $W*120/1440|bc) $(echo $H*156/900|bc) click 1\"
    m:0x44 + c:27
#    Control+Mod4 + r

# exit mcplot
\"xdotool mousemove $(echo $W*1307/1440|bc) $(echo $H*864/900|bc) click 1\" 
    m:0x44 + c:24
#    Control+Mod4 + q

# unzoom .2
\"xdotool mousemove $(echo $W*1036/1440|bc) $(echo $H*42/900|bc) click --repeat 2 1 restore\"
    m:0x44 + c:20
#    Control+Mod4 + minus

# zoom 5
\"xdotool mousemove $(echo $W*1251/1440|bc) $(echo $H*43/900|bc) click --repeat 2 1 restore\"
    m:0x44 + c:21
#    Control+Mod4 + equal

# show xy projection
\"xdotool mousemove $(echo $W*15/864 |bc ) $(echo $H*610/770|bc ) click 1\"
    m:0x44 + c:53
#    Control+Mod4 + x

# show yz projection
\"xdotool mousemove $(echo $W*183/1440|bc) $(echo $H*714/900|bc) click 1\"
    m:0x44 + c:29
#    Control+Mod4 + y

# show zx projection
\"xdotool mousemove $(echo $W*336/1440|bc) $(echo $H*714/900|bc) click 1\"
    m:0x44 + c:52
#    Control+Mod4 + z

# shift a bit up
\"xdotool mousemove $(echo $W*782/1440|bc) $(echo $H*42/900|bc) click 1 mousemove $(echo $W*900/1440|bc) $(echo $H*500/900|bc) click 1 restore\"
    m:0x44 + c:116
#    Control+Mod4 + Down

# shift a bit down
\"xdotool mousemove $(echo $W*782/1440|bc) $(echo $H*42/900|bc) click 1 mousemove $(echo $W*900/1440|bc) $(echo $H*400/900|bc) click 1 restore\"
    m:0x44 + c:111
#    Control+Mod4 + Up

# shift a bit left
\"xdotool mousemove $(echo $W*782/1440|bc) $(echo $H*42/900|bc) click 1 mousemove $(echo $W*850/1440|bc) $(echo $H*450/900|bc) click 1 restore\"
    m:0x44 + c:113
#    Control+Mod4 + Left

# shift a bit right
\"xdotool mousemove $(echo $W*782/1440|bc) $(echo $H*42/900|bc) click 1 mousemove $(echo $W*950/1440|bc) $(echo $H*450/900|bc) click 1 restore\"
    m:0x44 + c:114
#    Control+Mod4 + Right

# color temperature
\"xdotool mousemove $(echo $W*1400/1440|bc) $(echo $H*370/900|bc) click 1 mousemove $(echo $W*100/864|bc) $(echo $H*580/770|bc) click -repeat 2 1 mousemove $(echo $W*100/1440|bc) $(echo $H*100/900|bc) click 1\"
    m:0x44 + c:28
#    Control+Mod4 + t

# color material
\"xdotool mousemove $(echo $W*1400/1440|bc) $(echo $H*335/900|bc) click 1 mousemove $(echo $W*100/864|bc) $(echo $H*580/770|bc) click -repeat 2 1 mousemove $(echo $W*100/1440|bc) $(echo $H*100/900|bc) click 1\"
    m:0x44 + c:58
#    Control+Mod4 + m

# rotate
\"xdotool mousemove $(echo $W*200/1440|bc) $(echo $H*650/900|bc) click 1 mousemove $(echo $W*100/1440|bc) $(echo $H*100/900|bc) click 1\"
    m:0x44 + c:26
#    Control+Mod4 + e
### mcplotkeys end ###
"""
