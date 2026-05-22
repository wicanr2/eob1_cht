#!/bin/bash
X=$1
Y=$2
DELAY=${3:-1}
WID=$(DISPLAY=:0 xdotool search --class scummvm | head -1)
DISPLAY=:0 xdotool windowfocus $WID
sleep 0.3
DISPLAY=:0 xdotool mousemove --window $WID $X $Y
sleep 0.2
DISPLAY=:0 xdotool click --window $WID 3
sleep $DELAY
