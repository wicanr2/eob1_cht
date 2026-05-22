#!/bin/bash
WID=$(DISPLAY=:0 xdotool search --class scummvm | head -1)
echo "WID=$WID"
DISPLAY=:0 xdotool windowfocus $WID
sleep 1
for i in $(seq 1 80); do
    DISPLAY=:0 xdotool key --window $WID Escape
    sleep 0.15
done
sleep 3
DISPLAY=:0 import -window 0x60001b /mnt/c/Temp/eob1cht_12row_menu.png
ls -la /mnt/c/Temp/eob1cht_12row_menu.png
