#!/bin/bash
set -e
SRC="/mnt/c/Users/原來是個胖仔/scummvm_work/scummvm"
DST="/root/scummvm_work/scummvm"

# Copy updated files
cp "$SRC/devtools/create_kyradat/games.cpp" "$DST/devtools/create_kyradat/games.cpp"
cp "$SRC/devtools/create_kyradat/resources.cpp" "$DST/devtools/create_kyradat/resources.cpp"
cp "$SRC/devtools/create_kyradat/resources/eob1_dos_chinese.h" "$DST/devtools/create_kyradat/resources/eob1_dos_chinese.h"

# Rebuild create_kyradat
cd "$DST"
make devtools 2>&1 | tail -5

# Regenerate kyra.dat
cd /root/kyradat
rm -f kyra.dat KYRA.DAT
"$DST/devtools/create_kyradat/create_kyradat" KYRA.DAT 2>&1 | tail -5
ls -la /root/kyradat/

# Copy to game dir
cp /root/kyradat/KYRA.DAT /root/eob1cht/KYRA.DAT
ls -la /root/eob1cht/KYRA.DAT
