#!/bin/bash
# Usage: wsl_shot.sh <output_name>
NAME=${1:-eob1cht_current}
WID=$(DISPLAY=:0 xdotool search --class scummvm | head -1)
echo "WID=$WID"
HEX=$(printf '0x%x' $WID)
echo "HEX=$HEX"
DISPLAY=:0 import -window $HEX /mnt/c/Temp/${NAME}.png 2>&1
ls -la /mnt/c/Temp/${NAME}.png 2>&1
