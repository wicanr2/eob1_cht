#!/bin/bash
# Usage: wsl_key.sh <key> [delay]
KEY=$1
DELAY=${2:-0.5}
WID=$(DISPLAY=:0 xdotool search --class scummvm | head -1)
DISPLAY=:0 xdotool windowfocus $WID
sleep 0.2
DISPLAY=:0 xdotool key --window $WID $KEY
sleep $DELAY
