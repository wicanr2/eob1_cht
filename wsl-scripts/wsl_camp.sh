#!/bin/bash
WID=$(DISPLAY=:0 xdotool search --class scummvm | head -1)
echo "WID=$WID"
DISPLAY=:0 xdotool windowfocus $WID
sleep 1
# Try CAMP shortcut (C key)
DISPLAY=:0 xdotool key --window $WID c
sleep 2
DISPLAY=:0 import -window 0x60001b /mnt/c/Temp/eob1cht_camp.png
ls -la /mnt/c/Temp/eob1cht_camp.png
