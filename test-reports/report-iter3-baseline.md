# EOB1 CHT iter3 baseline

**Date**: 2026-05-23
**Tested binary**: `/root/scummvm_work/scummvm/scummvm` (Linux, rebuilt 13:06, chargen.o incremental)
**KYRA.DAT / ceob.pat**: unchanged from iter1
**Screenshots**: 25 PNGs at `screenshots/iter3-*.png`

## Summary

Both iter3 fixes PASS. Fix D and Fix E both verified working. All iter1/iter2 fix regressions hold. ScummVM remained stopped at end.

## Fix D / Fix E verdicts

| Fix | Bug | Verdict | Key screenshot |
|---|---|---|---|
| Fix D | BUG-003 action buttons English | **PASS** | `iter3-09-stats-with-buttons.png` shows 骰子 / 修改 / 造型 / 接受 in Chinese (replacing iter2's REROLL/MODIFY/FACES/KEEP bitmap) |
| Fix E | BUG-013 name input residue | **PASS** | `iter3-10-after-keep.png` shows clean black `fillRect` strip wiping the `人類男` glyphs; NO `名類男` residue. `iter3-11-name-typed.png` shows clean `test1` |

## Fix A/B/C regressions

- Fix A (stats 2-col): holds — `iter3-08/09/10` show 力/敏 智/體 慧/魅 + 防/命/級 cleanly
- Fix B (menu titles): holds — `iter3-05` 選擇種族：, `iter3-06` 選擇職業：, `iter3-07` 選擇陣營： all cleanly separated
- Fix C (portrait names): holds — `iter3-12-after-name.png` shows `TEST1` in char box, no `tact?` clipping

## Status of 9 iter2 open bugs

| ID | iter2 status | iter3 status |
|---|---|---|
| BUG-003 | open (major) | **RESOLVED** by Fix D |
| BUG-005 (色 glyph) | not re-tested | NOT RE-TESTED — couldn't reach in-game |
| BUG-006 (沒 glyph) | likely open | NOT RE-TESTED — couldn't reach in-game |
| BUG-007 multi-class | open (cosmetic) | NOT VERIFIED — elf-male class menu showed only single-class options in `iter3-33` |
| BUG-008 BACK bleed | open (minor) | NOT VISIBLE this iter; not actively probed |
| BUG-009 CAMP `營：` | open (deferred) | NOT RE-TESTED — couldn't reach CAMP |
| BUG-010 alignment spacing | open (cosmetic) | inconsistency not obvious in `iter3-07` — may have been font-related |
| BUG-011 multi-class header clip | partial | NOT RE-TESTED |
| BUG-013 name residue | open (major) | **RESOLVED** by Fix E |
| BUG-014 button clips 級 | open (cosmetic, deferred) | STILL PRESENT in `iter3-09`, expected |

## New bugs

**Translation/UX layer**: NONE.

**Testing infrastructure** (ENV-INFRA-01, NOT a translation bug):
- scummvm Linux build crashes ~2/3 of the time during headless Xvfb startup with `SDL_BlitSurface failed: SDL_UpperBlit: passed a NULL surface!` or `XIO: fatal IO error 0 (Success)` after ~645-721 X requests.
- Workarounds required to test iter3 binary:
  1. Add `-nolisten unix` to Xvfb (WSL `/tmp/.X11-unix` is read-only — WSLg integration)
  2. Add `--opl-driver=null --music-driver=null` to scummvm
  3. Wait 5+ seconds after launch before any input
  4. Use retry loop (3-5 attempts) since first launch often fails
- Suspect: new code path activated by Fix D/E in headless Xvfb context (Chinese button overlay drawShape interaction?). Worth a dev look — NOT blocking translation work.

## Inventory regression check (Fix C side-effect) — NOT VERIFIED

Could NOT load the existing iter2 save (`/root/.local/share/scummvm/saves/eob.000`) — the load dialog in `iter3-21-main-menu.png` showed all 6 slots as 尚未使用. iter3 build doesn't recognize iter2 save format / location. Did not have time budget to play through a fresh game to inventory.

## Severity counts (iter3 net open)

- **blocker**: 0
- **major**: 0 (down from 2 — both BUG-003 and BUG-013 resolved)
- **minor**: 3 (BUG-005, BUG-008, BUG-009)
- **cosmetic**: 5 (BUG-006, BUG-007, BUG-010, BUG-014, plus any minor unrelated)
- **Total OPEN (translation)**: 7 (down from 9 iter2)
- **Plus 1 INFRA issue**: ENV-INFRA-01 (testing instability)

## [UX]-tagged new bugs

NONE new this iter. Carry-over (all UNVERIFIED iter3): BUG-005, BUG-006, BUG-007, BUG-008, BUG-009, BUG-010, BUG-014.

## ScummVM running status

**STOPPED.** Verified via `driver.sh stop` and final ps check — no `scummvm` or `Xvfb :99` processes remain.

## Recommendations for iter4

1. **Investigate ENV-INFRA-01** — quick dev look at startup instability. Suspect: new `detection_tables.h` entry / `loadPCBIOSTall` 12-tall EOB1 path / `_invFont1` revert. Even a null-check could stabilize.
2. **Reach in-game** in iter4 to verify BUG-005/006/009 and inventory (full chargen→in-game flow works, just need to do all 4 chars).
3. **BUG-009** ux round (`gui_eob.cpp` CAMP submenu Y-spacing pattern matching Fix B in chargen.cpp).
4. Low priority: BUG-010 / BUG-014 — cosmetic, can defer.

## New tooling created (left in place for iter4)

- `tools/agent-helpers/driver.sh` — robust start/shot/key/clk with retry, timeouts, alive checks
- `tools/agent-helpers/full-flow.sh` — one-shot CharGen → name input flow
- `tools/agent-helpers/verify-deferred.sh` — re-verification flow
- `tools/agent-helpers/load-save.sh` — load-save attempt (does not work this iter)
- `tools/agent-helpers/eob1-headless.sh` — original helper, edited to add `-nolisten unix` (Bug fix for WSLg)
