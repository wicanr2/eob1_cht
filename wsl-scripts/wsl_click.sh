#!/bin/bash
# Usage: wsl_click.sh <x> <y> [delay_after]
X=$1
Y=$2
DELAY=${3:-1}
WID=$(DISPLAY=:0 xdotool search --class scummvm | head -1)
HEX=$(printf '0x%x' $WID)
DISPLAY=:0 xdotool windowfocus $WID
sleep 0.3
DISPLAY=:0 xdotool mousemove --window $WID $X $Y
sleep 0.2
DISPLAY=:0 xdotool click --window $WID 1
sleep $DELAY
