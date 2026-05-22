#!/bin/bash
set -e
cd /root/scummvm_work/scummvm
echo "=== configure with kyra+eob ==="
./configure --backend=sdl --disable-all-engines --enable-engine=kyra,eob 2>&1 | tail -10
echo
echo "=== make (incremental) ==="
make -j$(nproc) 2>&1 | tail -10
echo
ls -la scummvm
