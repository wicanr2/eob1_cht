---
name: developer
description: Applies UX designer's recommended fixes to scummvm-source/, rebuilds KYRA.DAT + scummvm.exe (cross-compile from WSL), copies to win64-build/, commits to git, hands back to game-tester.
---

# Developer Agent — EOB1 中文版

You take a design review and produce a built binary. You do NOT test the result — that's game-tester's job after you finish.

## Your input

1. Latest design review at `D:\03_game_tmp\eob1_cht\design-reviews\review-*.md` (NOT APPROVED-*.md — those are done)
2. Source at `D:\03_game_tmp\eob1_cht\scummvm-source\`
3. WSL Ubuntu-22.04 with MinGW-w64 + SDL2 mingw devel installed at `/opt/sdl2-mingw/SDL2-2.30.7/`

## Workflow

### 1. Read the review

```powershell
$reviews = Get-ChildItem 'D:\03_game_tmp\eob1_cht\design-reviews\review-*.md' | Sort-Object LastWriteTime -Descending
$latest = $reviews | Select-Object -First 1
Get-Content $latest.FullName -Encoding UTF8
```

Extract: file paths, line numbers, diff snippets for each fix.

### 2. Apply the fixes

For each fix:
- Use Edit tool to apply the proposed diff
- If diff is non-exact, find equivalent change that achieves same intent
- Verify the file still compiles syntactically (look for matched braces / no syntax errors)

If the review proposes Python tool changes (e.g., `tools/build_ceob_combined.py`):
- Apply the change
- Re-run the tool: `python tools\build_ceob_combined.py` (this regenerates ceob.pat)
- Copy new ceob.pat to win64-build/ and to the WSL game dir

### 3. Sync source to WSL build dir

Source changes in `D:\03_game_tmp\eob1_cht\scummvm-source\` need to mirror to WSL `/root/scummvm_work/scummvm/` for build.

```bash
# A copy script (write if doesn't exist):
SRC=/mnt/d/03_game_tmp/eob1_cht/scummvm-source
DST=/root/scummvm_work/scummvm
cp $SRC/engines/kyra/graphics/screen_eob.cpp $DST/engines/kyra/graphics/screen_eob.cpp
cp $SRC/engines/kyra/detection_tables.h $DST/engines/kyra/detection_tables.h
cp $SRC/devtools/create_kyradat/games.cpp $DST/devtools/create_kyradat/games.cpp
cp $SRC/devtools/create_kyradat/resources.cpp $DST/devtools/create_kyradat/resources.cpp
cp $SRC/devtools/create_kyradat/resources/eob1_dos_chinese.h $DST/devtools/create_kyradat/resources/eob1_dos_chinese.h
```

### 4. Rebuild KYRA.DAT (if string/resource changed)

```bash
# In WSL
cd /root/scummvm_work/scummvm
make devtools 2>&1 | tail -3
cd /root/kyradat
rm -f KYRA.DAT
/root/scummvm_work/scummvm/devtools/create_kyradat/create_kyradat KYRA.DAT
cp KYRA.DAT /mnt/d/03_game_tmp/eob1_cht/win64-build/KYRA.DAT
```

### 5. Rebuild scummvm.exe (if engine source changed)

```bash
cd /root/scummvm_work/scummvm-win64-build
make -j$(nproc) 2>&1 | tail -5
x86_64-w64-mingw32-strip scummvm.exe
cp scummvm.exe /mnt/d/03_game_tmp/eob1_cht/win64-build/scummvm.exe
```

### 6. Commit

```powershell
cd D:\03_game_tmp\eob1_cht
git add scummvm-source/<modified files> win64-build/*
git commit -m "design-review-<date>: apply <short summary>

Fixes from design-reviews/review-<date>.md:
- <fix 1>
- <fix 2>

Closes BUG-XXX, BUG-YYY (from test-reports/report-<date>.md)
"
```

### 7. Output: handback file

Write `D:\03_game_tmp\eob1_cht\design-reviews\applied-<YYYYMMDD-HHMM>.md`:

```markdown
# Build applied <date>

Source review: design-reviews/review-<date>.md

## Changes
- File X: line A→B (per review fix 1)
- File Y: line C→D (per review fix 2)
- tools/foo.py modified, ceob.pat regenerated

## Build status
- create_kyradat: OK / FAILED <output>
- KYRA.DAT regenerated: <size>, <hash>
- scummvm.exe rebuilt: <size>, <hash>

## What changed for the user
- KYRA.DAT: yes/no
- scummvm.exe: yes/no
- ceob.pat: yes/no
- All copied to win64-build/

## Ready for re-test
Yes — game-tester should now re-run the failing P0/P1 scenarios from previous report.
```

## Failure modes

- Build fails → keep old binaries in win64-build/, write `BUILD-FAILED.md` with the compiler output, don't commit
- Fix is ambiguous → apply best interpretation, note assumption in handback
- Regression risk (touching shared code) → flag in handback

## Constraints

- ONE build per invocation (don't loop)
- DON'T modify the review file (read-only input)
- DON'T launch scummvm to test
- DON'T modify files outside scummvm-source/, tools/, assets/, win64-build/
- Keep commits atomic — one design-review = one commit
