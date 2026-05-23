# EOB1 CHT 測試報告 iter2 baseline

**Date**: 2026-05-23
**Tested binary**: `/root/scummvm_work/scummvm/scummvm` (SHA-256 `26aa28bee4812800...`, 43.6 MB, rebuilt 2026-05-23)
**KYRA.DAT / ceob.pat**: unchanged from iter1
**Screenshots**: 43 frames at `screenshots/iter2-*.png`

## TL;DR

**All three applied fixes PASS verification.** 12 iter1 bugs → 9 net open: 3 resolved by fixes (BUG-001/002/004), 1 auto-resolved bonus (BUG-012), 2 new (BUG-013/014), 8 carry-over.

## Fix verification (Pass/Fail)

| Fix | Bug fixed | Verdict | Key screenshot |
|---|---|---|---|
| **Fix A** | BUG-002 (BLOCKER) stats overlap | ✅ **PASS** | `iter2-20-stats-FIX-A.png` — 2 cols × 3 rows: 力9 敏15 / 智5 體12 / 慧14 魅12 + 防：9 命：16 級：3. Zero overlap, fully readable. |
| **Fix B** | BUG-001 menu title overlap | ✅ **PASS** | `iter2-16-race-menu-FIX-B.png`, `iter2-17-class-menu-FIX-B.png`, `iter2-19-alignment-menu-FIX-B.png` — `選擇種族：/職業：/陣營：` cleanly separated from first item across all three menus. |
| **Fix C** | BUG-004 portrait names | ✅ **PASS** | `iter2-31-game-start-FIX-C.png` — `TEST1/TEST2/TEST3/TEST4` all render cleanly; digits 1/2/3 no longer `?`. Also verified on loaded save (`iter2-02-ingame-portraits-FIX-C.png`, `ANR3/ANR2/ANR4/ANR2` clean). |

## Status of 12 iter1 bugs

| ID | iter1 sev | iter2 status | Note |
|---|---|---|---|
| BUG-001 | major | **RESOLVED** | Fix B |
| BUG-002 | **BLOCKER** | **RESOLVED** | Fix A |
| BUG-003 | major | open | REROLL/MODIFY/FACES/KEEP/BACK/PLAY/+/-/OK all still English — bitmap sprites in PAK, not source |
| BUG-004 | major | **RESOLVED** | Fix C |
| BUG-005 | minor | not re-tested | Couldn't reach 遊戲選項 > 踢出角色 due to click-target issues in time budget; not in Fix scope |
| BUG-006 | cosmetic | likely still open | `沒` glyph still appears unusual in `iter2-39-game-options.png` |
| BUG-007 | cosmetic | open | Multi-class strings not encountered this iter (didn't pick multi-class) |
| BUG-008 | minor | open | `iter2-18-class-menu.png` shows lower edge of menu has bleed-through |
| BUG-009 | minor | open (deferred as expected) | `營：`/`偏好：` titles still overlap first item — lives in `gui_eob.cpp`, NOT touched by Fix B (`chargen.cpp`). See `iter2-03/04`. |
| BUG-010 | cosmetic | open | `守序善良` flush vs `中立 善良` inconsistent spacing — `iter2-19` |
| BUG-011 | minor | partially resolved | Race+class header reads cleanly post-Fix A; multi-class clipping not re-tested |
| BUG-012 | minor | **RESOLVED** (auto) | Race+class+stats squeeze gone as side-effect of Fix A 2-col layout |

## New bugs introduced in iter2

### BUG-013 [UX major] Name input overlays underlying race-sex string
- **Scene**: CharGen name entry step
- **Screenshot**: `iter2-28-name-typed.png`
- **Observation**: Field shows `名類男test1` instead of just `test1` — the `人類男` from the previous CharGen step is not cleared/overpainted by the name input box. Position 0 gets the prompt char `名`, but positions 1-2 keep `類男` and `test1` follows.
- **Note**: Latent in iter1 too (`iter1-26-name-typed.png` shows `名類男est ` pattern), but was masked by BUG-002 blocker dominating attention. Now clearly visible after Fix A makes the rest of the screen clean.
- **Hypothesis**: Name input prompt doesn't blit-clear the text strip before drawing. Likely 1-line fix to add a clear-rect before name field draw.

### BUG-014 [UX cosmetic] Action button panel overlaps 級 stat
- **Scene**: CharGen stats screen, when REROLL/MODIFY/FACES/KEEP panel visible
- **Screenshot**: `iter2-22-face-picked.png`
- **Observation**: Button panel at x~460-625, y~350-440 covers right portion of `魅` value (row 3 col 2) and `級` label+value (row 4 right). Stats are fully visible at face-pick step (`iter2-21-stats-full.png`, no buttons yet) and after KEEP commits (`iter2-23/29`, buttons gone). Cosmetic — player sees stats at other moments.
- **Hypothesis**: Fix A's stats column 2 X position (~470) collides with button panel left edge. Either shrink/move panel, or shift stats col 2 to x~440.

## Severity counts (iter2 net open)

- **blocker**: 0 (was 1)
- **major**: 2 (BUG-003 carry, BUG-013 new) — down from 3
- **minor**: 3 (BUG-008, 009, 011) — down from 5
- **cosmetic**: 5 (BUG-005, 006, 007, 010, 014)
- **Total OPEN**: 9 (down from 12)
- **Zero new blocker/major regressions** from fixes.

## [UX]-tagged bugs for next ux-designer round

**Carry-over from iter1** (priority for layout work):
- BUG-003 — CharGen action buttons still English (bitmap sprites, separate asset workstream)
- BUG-005 — 「色」glyph (not re-verified this iter)
- BUG-006 — 「沒」glyph
- BUG-007 — Multi-class format inconsistency
- BUG-008 — BACK button redraw bleed
- **BUG-009** — CAMP `營：` / 偏好`偏好：` overlap. **Highest priority next iter** — same Y-spacing fix pattern as Fix B but in `gui_eob.cpp` (3-5 locations of `GI_EOB2 && ZH_TWN`).
- BUG-010 — Alignment spacing inconsistency
- BUG-011 — Multi-class header clipping (not re-tested)

**New iter2**:
- **BUG-013** — Name input overlays race-sex string (`iter2-28`). Major. 1-line blit-clear fix likely.
- **BUG-014** — Action button panel clips 級 (`iter2-22`). Cosmetic.

## Coverage gaps (could not test this iter)

- **Inventory screen** — engine kept exiting on portrait-click attempts (2 separate restarts). Could not verify the `_invFont1` removal from FID_CHINESE_FNT chain didn't introduce a regression in Chinese item descriptions / character sheet rendering. **Open question carried to next iter.**
- **BUG-005 「色」glyph** in 踢出角色 — couldn't reach 遊戲選項 due to click-target issues + time budget.
- **Quit confirm dialog** — was passing in iter1, not impacted by Fix A/B/C scope.

## ScummVM stability

- 3 scummvm sessions, 4 restart cycles (~30s each).
- Clean exits (no SDL fatal / no segfault in log) on:
  - Escape in CAMP submenu
  - Double-click on portrait
- Same exit-to-launcher-then-launcher-crashes pattern as iter1. No crashes during gameplay/CharGen.
- Save folder `/root/.local/share/scummvm/saves/` gets wiped on exit; iter1 saves backed up to `saves-iter1-backup/`.

## Final state

- **ScummVM stopped** via `eob1-headless.sh stop`. No `scummvm`/`Xvfb` processes remain.
- 43 PNGs saved at `D:\03_game_tmp\eob1_cht\test-reports\screenshots\iter2-*.png` (key shots tagged `-FIX-A/-FIX-B/-FIX-C`).

## Recommendations for next iter

1. **Highest priority**: BUG-009 family — patch `gui_eob.cpp` CAMP submenu Y-spacing (3-5 locations of `GI_EOB2 && ZH_TWN` → `ZH_TWN`, same pattern as Fix B did in `chargen.cpp`).
2. **Medium**: BUG-013 — name input clear-rect before draw (~1 line of code).
3. **Medium**: BUG-014 — action button panel position vs stats col 2.
4. **Low**: BUG-003 — bitmap button assets (separate asset workstream).
5. **Open question to verify**: Inventory screen Chinese rendering after `_invFont1` revert.
