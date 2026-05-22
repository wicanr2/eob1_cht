#!/bin/bash
pkill -9 scummvm 2>/dev/null
sleep 1
# Detach properly using setsid so scummvm survives WSL exit
DISPLAY=:0 setsid -f /root/scummvm_work/scummvm/scummvm \
    --extrapath=/root/eob1cht \
    --path=/root/eob1cht \
    --auto-detect \
    > /mnt/c/Temp/scummvm_run.log 2>&1
echo "launched, waiting 8s for window..."
sleep 8
pgrep -af scummvm | head -3
echo ---windows---
DISPLAY=:0 xwininfo -root -tree 2>&1 | grep -A1 -B1 -i scummvm
