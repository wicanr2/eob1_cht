#!/bin/bash
set -e
cd /root/scummvm_work/scummvm
echo "=== configure (kyra engine only, SDL2 backend) ==="
./configure --backend=sdl --disable-all-engines --enable-engine=kyra 2>&1 | tail -15
echo
echo "=== make (this will take 5-15 min) ==="
make -j$(nproc) 2>&1 | tail -10
echo
ls -la scummvm
