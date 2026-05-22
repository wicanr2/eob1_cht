#!/bin/bash
set -e
SRC="/mnt/c/Users/原來是個胖仔/scummvm_work/scummvm"
DST="/root/scummvm_work/scummvm"

# 1. Copy modified engine source + new ceob.pat
cp "$SRC/engines/kyra/graphics/screen_eob.cpp" "$DST/engines/kyra/graphics/screen_eob.cpp"
cp /mnt/c/Users/原來是個胖仔/scummvm_work/ceob.pat /root/eob1cht/ceob.pat
echo "files copied"

# 2. Incremental build
cd "$DST"
make -j$(nproc) 2>&1 | tail -5

# 3. Kill old scummvm and relaunch
pkill -9 scummvm 2>/dev/null
sleep 1
DISPLAY=:0 setsid -f /root/scummvm_work/scummvm/scummvm \
    --extrapath=/root/eob1cht \
    --path=/root/eob1cht \
    --auto-detect \
    > /mnt/c/Temp/scummvm_run.log 2>&1
sleep 6
pgrep -af scummvm | head -3
echo ---windows---
DISPLAY=:0 xwininfo -root -tree 2>&1 | grep -B1 -i scummvm | head -5
