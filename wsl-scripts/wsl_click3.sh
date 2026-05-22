#!/bin/bash
# Usage: wsl_click3.sh <x> <y> [delay_after]
# Uses absolute screen coords offset to window
X=$1
Y=$2
DELAY=${3:-1}
WID=$(DISPLAY=:0 xdotool search --class scummvm | head -1)
DISPLAY=:0 xdotool windowactivate --sync $WID
sleep 0.3
eval $(DISPLAY=:0 xdotool getwindowgeometry --shell $WID)
ABSX=$((X + WINDOW_X))
ABSY=$((Y + WINDOW_Y))
# But scummvm coords are usually offset by titlebar/border; lets check.
echo "Moving to abs ($ABSX, $ABSY) for window-relative ($X, $Y)"
DISPLAY=:0 xdotool mousemove $ABSX $ABSY
sleep 0.3
DISPLAY=:0 xdotool click 1
sleep $DELAY
