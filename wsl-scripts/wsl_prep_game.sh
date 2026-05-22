#!/bin/bash
set -e
GAME_SRC="/mnt/d/SteamLibrary/steamapps/common/Forgotten Realms The Archives - Collection One/games/Eye of the Beholder ENG/GAME/EYE"
GAME_DST="/root/eob1cht"

mkdir -p "$GAME_DST"
echo "=== Copy game files (skip if already done) ==="
if [ ! -f "$GAME_DST/EOB.EXE" ]; then
    cp -v "$GAME_SRC"/*.EXE "$GAME_SRC"/*.PAK "$GAME_SRC"/*.OVL "$GAME_SRC"/*.FNT "$GAME_SRC"/*.SAV "$GAME_SRC"/*.TMP "$GAME_DST"/ 2>&1 | tail -5
fi
echo
echo "=== Copy ceob.pat ==="
cp -v /mnt/c/Users/原來是個胖仔/scummvm_work/ceob.pat "$GAME_DST/ceob.pat"

echo
echo "=== Copy kyra.dat ==="
cp -v /tmp/kyradat_out/kyra.dat "$GAME_DST/kyra.dat"

echo
echo "=== List game dir ==="
ls -la "$GAME_DST"

echo
echo "=== ScummVM detection test ==="
/root/scummvm_work/scummvm/scummvm --extrapath="$GAME_DST" --detect --path="$GAME_DST" 2>&1 | head -30
