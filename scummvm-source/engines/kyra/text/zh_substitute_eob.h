/* ScummVM EOB1 繁體中文化 — Display-time substitution table
 *
 * For LEVEL.INF script-embedded strings that cannot be in-place patched
 * (Chinese cp950 bytes typically exceed original ASCII length, breaking
 * bytecode offsets).
 *
 * Approach: hook engine text-display path; for EOB1 ZH_TWN, look up EN
 * string in static table; if match, return ZH; else pass through.
 *
 * Pattern adapted from u6-cht (Ultima VI 繁中化) Plan B load-time
 * substitution methodology.
 */
#ifndef KYRA_ZH_SUBSTITUTE_EOB_H
#define KYRA_ZH_SUBSTITUTE_EOB_H

#include "common/scummsys.h"

namespace Kyra {

// Returns Big5 cp950 ZH translation if `en` is in the EOB1 lookup table.
// Returns `en` unchanged otherwise (safe for LoL and other engines).
// Caller decides when to invoke (typically inside printMessage / printDialogueText).
const char *zhSubstituteEoB(const char *en);

} // End of namespace Kyra

#endif
