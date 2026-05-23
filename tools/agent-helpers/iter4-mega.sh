#!/bin/bash
# Mega flow — full clean reboot → CharGen → name input → multi-class test
# All inside ONE wsl bash session to avoid X11 race that kills scummvm
# every ~650 requests when xdotool reconnects via separate wsl calls.
set -u
T=/mnt/d/03_game_tmp/eob1_cht/tools/agent-helpers/test-iter3.sh
S=/mnt/d/03_game_tmp/eob1_cht/test-reports/screenshots
step() { echo "=== $* ==="; }

step "stop & start"
bash $T stop >/dev/null 2>&1 || true
sleep 1
bash $T start || exit 1
sleep 2

step "skip intro x35"
for i in $(seq 1 35); do
    bash $T alive >/dev/null 2>&1 || break
    bash $T key space >/dev/null 2>&1
    sleep 0.18
done

step "click 完畢 (420,178)"
bash $T clicks 420 178
sleep 0.5

step "click 取消 (430,355)"
bash $T clicks 430 355
sleep 0.5

step "click 開始新隊伍 (200,460)"
bash $T clicks 200 460
sleep 1

step "click char box 0 (64,160)"
bash $T clicks 64 160
sleep 0.5

step "race row1 — human male"
bash $T clicks 400 200
sleep 0.5

step "class row1 — warrior"
bash $T clicks 400 200
sleep 0.5

step "alignment row1"
bash $T clicks 400 200
sleep 1

# Stats screen with portrait selector — 5 portraits in a row at top
# Need to pick a portrait first. iter3 used Return for face commit then K for KEEP.
step "shot at stats+portrait phase"
bash $T shot $S/iter4-m01-stats-portrait-select.png

step "Return to confirm default portrait"
bash $T key Return
sleep 0.5
bash $T shot $S/iter4-m02-after-return.png

step "K to KEEP (advance to name input via Fix D)"
bash $T key k
sleep 0.6
bash $T shot $S/iter4-m03-name-input-INITIAL.png

# CRITICAL: snap the requested bug screenshot
bash $T shot $S/iter4-bug-name-input.png
sleep 0.2

step "type test1"
bash $T key t e s t 1
sleep 0.3
bash $T shot $S/iter4-m04-name-typed.png

step "backspace x2"
bash $T key BackSpace BackSpace
sleep 0.3
bash $T shot $S/iter4-m05-after-backspace.png

step "Return confirm"
bash $T key Return
sleep 1
bash $T shot $S/iter4-m06-after-name-return.png

# Box 1 — elf male path for multi-class (Fix F)
step "click box 1 (64,280)"
bash $T clicks 64 280
sleep 0.6
bash $T shot $S/iter4-m07-box1-race.png

step "race elf male — try y=240"
bash $T clicks 400 240
sleep 0.5
bash $T shot $S/iter4-m08-elf-class-menu.png

# Fix F test: elf male class menu should show 戰／法 multi-class options
# Snap just in case the menu has multiple rows showing 戰／法 etc.
step "shot elf class menu"
bash $T shot $S/iter4-m09-elf-classes.png

echo "=== FINAL ==="
bash $T alive
bash $T logtail
