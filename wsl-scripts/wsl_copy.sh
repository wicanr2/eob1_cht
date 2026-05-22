#!/bin/bash
set -e
SRC="/mnt/c/Users/原來是個胖仔/scummvm_work/scummvm"
DST="/root/scummvm_work/scummvm"
echo "SRC=$SRC"
echo "DST=$DST"
cp "$SRC/engines/kyra/detection_tables.h" "$DST/engines/kyra/detection_tables.h"
cp "$SRC/engines/kyra/graphics/screen_eob.cpp" "$DST/engines/kyra/graphics/screen_eob.cpp"
cp "$SRC/devtools/create_kyradat/resources/eob1_dos_chinese.h" "$DST/devtools/create_kyradat/resources/eob1_dos_chinese.h"
cp "$SRC/devtools/create_kyradat/resources.cpp" "$DST/devtools/create_kyradat/resources.cpp"
cd "$DST"
echo "--- diff stat ---"
git diff --stat
