#!/bin/bash
X=$1
Y=$2
DELAY=${3:-1}
WID=$(DISPLAY=:0 xdotool search --class scummvm | head -1)
# Activate (raise + focus) instead of just focus
DISPLAY=:0 xdotool windowactivate $WID 2>/dev/null
sleep 0.5
DISPLAY=:0 xdotool mousemove --window $WID $X $Y
sleep 0.2
# Use --clearmodifiers + button release sequencing
DISPLAY=:0 xdotool mousedown --window $WID 1
sleep 0.1
DISPLAY=:0 xdotool mouseup --window $WID 1
sleep $DELAY
