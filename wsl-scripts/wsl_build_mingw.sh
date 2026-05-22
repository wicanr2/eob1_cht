#!/bin/bash
set -e
cd /root/scummvm_work/scummvm

SDL_PREFIX=/opt/sdl2-mingw/SDL2-2.30.7/x86_64-w64-mingw32
export PATH="$SDL_PREFIX/bin:$PATH"

# Make a clean win64 build dir alongside the existing linux build
WINBLD=/root/scummvm_work/scummvm-win64-build
mkdir -p "$WINBLD"
cd "$WINBLD"

echo "=== configure (Win64 cross, kyra+eob only) ==="
/root/scummvm_work/scummvm/configure \
    --host=x86_64-w64-mingw32 \
    --with-sdl-prefix=$SDL_PREFIX \
    --backend=sdl \
    --disable-all-engines --enable-engine=kyra,eob \
    --disable-translation \
    --disable-flac --disable-vorbis --disable-mad \
    --disable-fluidsynth --disable-freetype2 --disable-jpeg --disable-png \
    --disable-mt32emu \
    2>&1 | tail -25

echo
echo "=== make (8 jobs, ~5-10 min) ==="
make -j$(nproc) 2>&1 | tail -15

echo
ls -la scummvm.exe 2>/dev/null || ls -la *.exe 2>/dev/null
