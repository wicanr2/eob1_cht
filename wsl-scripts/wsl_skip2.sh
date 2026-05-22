#!/bin/bash
WID=$(DISPLAY=:0 xdotool search --class scummvm | head -1)
HEX=$(printf '0x%x' $WID)
echo "WID=$WID HEX=$HEX"
DISPLAY=:0 xdotool windowfocus $WID
sleep 1
# Spam space/enter (skip cinematic screens) — NOT escape (which exits to launcher)
for i in $(seq 1 60); do
    DISPLAY=:0 xdotool key --window $WID space
    sleep 0.2
    DISPLAY=:0 xdotool key --window $WID Return
    sleep 0.2
done
sleep 3
DISPLAY=:0 import -window $HEX /mnt/c/Temp/after_intro.png
ls -la /mnt/c/Temp/after_intro.png
