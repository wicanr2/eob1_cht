#!/bin/bash
set -e
WINBLD=/root/scummvm_work/scummvm-win64-build
SDL_PREFIX=/opt/sdl2-mingw/SDL2-2.30.7/x86_64-w64-mingw32

# Destination on Windows
DST="/mnt/c/Users/原來是個胖仔/eob1cht/scummvm-win"
mkdir -p "$DST"

# Strip the binary to reduce size dramatically
echo "=== Stripping binary ==="
ls -la "$WINBLD/scummvm.exe"
x86_64-w64-mingw32-strip "$WINBLD/scummvm.exe"
ls -la "$WINBLD/scummvm.exe"

# Copy files
cp "$WINBLD/scummvm.exe" "$DST/"
cp "$SDL_PREFIX/bin/SDL2.dll" "$DST/"
# Copy our game data
cp /root/eob1cht/ceob.pat "$DST/ceob.pat"
cp /root/eob1cht/KYRA.DAT "$DST/KYRA.DAT"
# kyra.dat MUST be next to scummvm OR in extrapath; we'll put both ways

echo
echo "=== Final Windows package ==="
ls -la "$DST/"
