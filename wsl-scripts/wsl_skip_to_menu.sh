#!/bin/bash
WID=$(DISPLAY=:0 xdotool search --class scummvm | head -1)
echo "WID=$WID"
DISPLAY=:0 xdotool windowfocus $WID
sleep 1
# Spam space/enter (skip cinematic screens) — NOT escape (which exits to launcher)
for i in $(seq 1 80); do
    DISPLAY=:0 xdotool key --window $WID space
    sleep 0.2
    DISPLAY=:0 xdotool key --window $WID Return
    sleep 0.2
done
sleep 3
DISPLAY=:0 import -window 0x60001b /mnt/c/Temp/eob1cht_12row_menu.png
ls -la /mnt/c/Temp/eob1cht_12row_menu.png
