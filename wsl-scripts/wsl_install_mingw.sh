#!/bin/bash
set -e
echo "=== Installing MinGW-w64 cross-compiler + SDL2 mingw libs ==="
DEBIAN_FRONTEND=noninteractive apt-get install -y \
    mingw-w64 \
    libz-mingw-w64-dev \
    2>&1 | tail -5

echo
echo "=== Downloading SDL2 mingw devel (precompiled binaries) ==="
mkdir -p /opt/sdl2-mingw
cd /opt/sdl2-mingw
if [ ! -f SDL2-devel-2.30.7-mingw.tar.gz ]; then
    wget -q https://github.com/libsdl-org/SDL/releases/download/release-2.30.7/SDL2-devel-2.30.7-mingw.tar.gz
fi
if [ ! -d SDL2-2.30.7 ]; then
    tar xf SDL2-devel-2.30.7-mingw.tar.gz
fi
echo "SDL2 ready at /opt/sdl2-mingw/SDL2-2.30.7/x86_64-w64-mingw32/"
ls /opt/sdl2-mingw/SDL2-2.30.7/x86_64-w64-mingw32/include/SDL2 | head -5
