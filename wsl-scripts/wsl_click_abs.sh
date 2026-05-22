#!/bin/bash
X=$1
Y=$2
DELAY=${3:-1}
WID=$(DISPLAY=:0 xdotool search --class scummvm | head -1)
DISPLAY=:0 xdotool windowfocus $WID
sleep 0.3
WX=$(DISPLAY=:0 xdotool getwindowgeometry $WID 2>/dev/null | grep Position | grep -oE '[0-9]+,[0-9]+' | head -1 | cut -d, -f1)
WY=$(DISPLAY=:0 xdotool getwindowgeometry $WID 2>/dev/null | grep Position | grep -oE '[0-9]+,[0-9]+' | head -1 | cut -d, -f2)
ABSX=$((WX + X))
ABSY=$((WY + Y))
echo "Window at ($WX, $WY), clicking abs ($ABSX, $ABSY) for game ($X, $Y)"
DISPLAY=:0 xdotool mousemove $ABSX $ABSY
sleep 0.2
DISPLAY=:0 xdotool getmouselocation
DISPLAY=:0 xdotool click 1
sleep $DELAY
