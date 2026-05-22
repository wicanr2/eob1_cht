#!/bin/bash
# Usage: wsl_click2.sh <x> <y> [delay_after]
X=$1
Y=$2
DELAY=${3:-1}
WID=$(DISPLAY=:0 xdotool search --class scummvm | head -1)
DISPLAY=:0 xdotool windowfocus $WID
sleep 0.3
# Move mouse globally (not just to the window) for scummvm to register
DISPLAY=:0 xdotool mousemove $X $Y
sleep 0.3
DISPLAY=:0 xdotool click 1
sleep $DELAY
