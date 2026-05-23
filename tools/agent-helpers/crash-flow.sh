#!/bin/bash
# All-in-one flow for crash repro — single session, no inter-process Bash spawn overhead.
set -u
D=/mnt/d/03_game_tmp/eob1_cht/tools/agent-helpers/crash-repro.sh
S=/tmp/eob1-crash/shots
mkdir -p $S

step() {
    echo "=== $* ==="
    $D alive >/dev/null 2>&1 || { echo "DEAD"; $D logtail; exit 1; }
}

$D stop >/dev/null 2>&1
sleep 1
$D start || exit 1
$D shot $S/00-boot.png

# Skip intro: spam Escape
for i in $(seq 1 25); do
    $D alive >/dev/null 2>&1 || { echo "DIED during intro spam at i=$i"; $D logtail; exit 1; }
    $D key Escape >/dev/null 2>&1
    sleep 0.08
done
$D shot $S/01-after-intro.png
step "after-intro"

# Dismiss load-error done
$D clk 430 160 >/dev/null
sleep 0.3
$D shot $S/02-after-done.png
step "after-done"

# Cancel load dialog
$D clk 430 355 >/dev/null
sleep 0.3
$D shot $S/03-after-cancel.png
step "after-cancel"

# Click 開始新隊伍
$D clk 270 460 >/dev/null
sleep 1
$D shot $S/04-chargen.png
step "chargen-start"

# CRASH BUG A: Click portrait box 0 (top-left empty slot)
echo "=== BUG A: click portrait box 0 (64,160) ==="
$D clk 64 160 >/dev/null
sleep 0.5
$D shot $S/05-race-menu-or-crash.png
if $D alive >/dev/null 2>&1; then
    echo "Survived box click — now in race menu"
    $D shot $S/05b-race-menu.png
    # Click first race option to trigger another _invFont1 path
    echo "=== Click first race option ==="
    $D clk 400 200 >/dev/null
    sleep 0.5
    $D shot $S/06-after-race.png
    if $D alive >/dev/null 2>&1; then
        echo "Survived race click"
    else
        echo "DIED after race click"
        $D logtail
        exit 0
    fi
else
    echo "DIED after portrait box 0 click"
    $D logtail
    exit 0
fi

# Continue past race + class + alignment, stats roll, FACE picker (which uses _invFont1)
echo "=== Pick first class ==="
$D clk 400 200 >/dev/null
sleep 0.5
$D shot $S/07-alignment-menu.png
step "alignment-menu"

echo "=== Pick first alignment ==="
$D clk 400 200 >/dev/null
sleep 1
$D shot $S/08-stats-rolled.png
step "stats-rolled"

# stats screen — try clicking on the face area at right side (large portrait ~280,8 native → SDL 560,16)
# Actually check the face picker — there's a FACES button that opens menu
# Look at stats screen, then click FACES button (label position TBD)
echo "=== Click FACES button area (right of stats) ==="
# In chargen stats screen the buttons are at native (224,156)/(264,156)/(224,172)/(264,172) which is FACES at 224,172 → SDL (448,344)
$D clk 448 344 >/dev/null
sleep 0.5
$D shot $S/09-face-menu.png
if ! $D alive >/dev/null 2>&1; then
    echo "CRASH after FACES click"
    $D logtail
    exit 0
fi

echo "=== Click a face in face picker ==="
$D clk 200 100 >/dev/null
sleep 0.5
$D shot $S/10-face-picked.png
if ! $D alive >/dev/null 2>&1; then
    echo "CRASH after face pick"
    $D logtail
    exit 0
fi

echo "=== Press K for KEEP ==="
$D key k >/dev/null
sleep 0.5
$D shot $S/11-keep-pressed.png
if ! $D alive >/dev/null 2>&1; then
    echo "CRASH after KEEP"
    $D logtail
    exit 0
fi

echo "=== Type name ==="
$D key t e s t 1 >/dev/null
sleep 0.3
$D key Return >/dev/null
sleep 0.5
$D shot $S/12-name-entered.png
if ! $D alive >/dev/null 2>&1; then
    echo "CRASH after name"
    $D logtail
    exit 0
fi

echo "=== Press Escape to back out of stats view ==="
$D key Escape >/dev/null
sleep 0.5
$D shot $S/13-back-to-chargen.png
step "back-to-chargen"

# Create chars 2/3/4 quickly via clicking other boxes
# Box layout (SDL): 0=(64,160) 1=(192,160) 2=(64,224) 3=(192,224)
for i in 1 2 3; do
    case $i in
        1) X=192; Y=160 ;;
        2) X=64; Y=224 ;;
        3) X=192; Y=224 ;;
    esac
    echo "=== Box $i at ($X,$Y) ==="
    $D clk $X $Y >/dev/null
    sleep 0.5
    # race
    $D clk 400 200 >/dev/null
    sleep 0.3
    # class
    $D clk 400 200 >/dev/null
    sleep 0.3
    # alignment
    $D clk 400 200 >/dev/null
    sleep 0.5
    # KEEP
    $D key k >/dev/null
    sleep 0.3
    # name
    $D key c h$i a r >/dev/null
    sleep 0.2
    $D key Return >/dev/null
    sleep 0.5
    $D shot $S/14-box-$i-done.png
    if ! $D alive >/dev/null 2>&1; then
        echo "DIED creating char $i"
        $D logtail
        exit 0
    fi
done

echo "=== Press P to PLAY (start game) ==="
$D key p >/dev/null
sleep 2
$D shot $S/15-in-game.png
if ! $D alive >/dev/null 2>&1; then
    echo "CRASH on game start"
    $D logtail
    exit 0
fi

echo "=== BUG B: Click portrait 0 in-game (right side panel, native ~16,8 → SDL 32,16, but inventory panel x=176+ in native = 352+ SDL) ==="
# In-game portrait positions: charBoxCoords.boxX[0] = 16, boxY[0] = 8 — but native 0,0 to 176,144 is dungeon view, 176-320 is right panel
# Actually portrait in main game native coords: x={176, 240}, y={8, 32, 56, 80, 104, 128} (3x2 grid for EOB1)
# Box 0 at (176, 8) → SDL (352, 16)
$D clk 352 30 >/dev/null
sleep 0.5
$D shot $S/16-portrait-click.png
if ! $D alive >/dev/null 2>&1; then
    echo "CRASH on portrait click (BUG B confirmed)"
    $D logtail
    exit 0
fi

echo "=== Click portrait 0 AGAIN to enter inventory ==="
$D clk 352 30 >/dev/null
sleep 0.5
$D shot $S/17-portrait-double.png
if ! $D alive >/dev/null 2>&1; then
    echo "CRASH on second portrait click (BUG B variant)"
    $D logtail
    exit 0
fi

echo "FLOW COMPLETE without crash"
$D logtail
