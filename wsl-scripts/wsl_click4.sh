#!/bin/bash
# Usage: wsl_click4.sh <x> <y> [delay_after]
X=$1
Y=$2
DELAY=${3:-1}
WID=$(DISPLAY=:0 xdotool search --class scummvm | head -1)
DISPLAY=:0 xdotool windowactivate --sync $WID
sleep 0.5
DISPLAY=:0 xdotool windowfocus --sync $WID
sleep 0.3
DISPLAY=:0 xdotool mousemove --window $WID $X $Y
sleep 0.3
# Try mousedown, hold, mouseup for SDL
DISPLAY=:0 xdotool mousedown --window $WID 1
sleep 0.15
DISPLAY=:0 xdotool mouseup --window $WID 1
sleep $DELAY
