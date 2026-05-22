"""Re-encode ceob.pat from EOB2 CHINFONT.FNT cropped to 10 rows.

EOB2 glyphs are 16x14 — the actual character strokes occupy roughly rows 2-12
in the canvas (top/bottom 1-2 rows are normally blank for kerning).
Cropping 14 → 10 by removing top 2 + bottom 2 rows keeps the main strokes
intact and saves 4 pixels of vertical space.

Output format identical to existing ceob.pat (Big5Font::loadPrefixedRaw):
  Repeating: [BE uint16 codepoint][2 * height bytes bitmap]  terminator 0xFFFF.
"""
import sys, struct
from pathlib import Path

SRC_PATH = r"E:\dos1866\eob2\CHINFONT.FNT"
DST_PATH = r"C:\Users\原來是個胖仔\scummvm_work\ceob.pat"
GLYPH_BYTES = 30   # encrypted format: 2-byte cp + 28-byte bitmap
SRC_ROWS = 14
NEW_ROWS = 12
TOP_TRIM = 1       # rows trimmed from top (bottom_trim = 14-NEW_ROWS-TOP_TRIM = 1)
# So we keep rows [TOP_TRIM .. TOP_TRIM+NEW_ROWS) = [1 .. 13)

def main():
    data = Path(SRC_PATH).read_bytes()
    assert len(data) % GLYPH_BYTES == 0
    n = len(data) // GLYPH_BYTES
    out = bytearray()
    seen = set()
    written = 0
    skipped_dups = 0
    skipped_no_high = 0
    for i in range(n):
        block = data[i*GLYPH_BYTES:(i+1)*GLYPH_BYTES]
        lo, hi = block[0], block[1]
        cp = (hi << 8) | lo
        if not (cp & 0x8000):
            skipped_no_high += 1
            continue
        if cp in seen:
            skipped_dups += 1
            continue
        seen.add(cp)
        enc = block[2:]
        # Decrypt all 28 bytes
        dec = bytearray(28)
        for k in range(28):
            dec[k] = enc[k] ^ (lo if k % 2 == 0 else hi)
        # Crop to rows [TOP_TRIM .. TOP_TRIM+NEW_ROWS)
        cropped = bytearray()
        for r in range(TOP_TRIM, TOP_TRIM + NEW_ROWS):
            cropped += dec[r*2:r*2+2]
        out += struct.pack(">H", cp)
        out += bytes(cropped)
        written += 1
    out += b"\xff\xff"
    Path(DST_PATH).write_bytes(out)
    print(f"Wrote {DST_PATH}: {written} glyphs at 16x{NEW_ROWS}, {len(out)} bytes (skipped {skipped_dups} dups, {skipped_no_high} no-high)")
    # Quick render check for 中 (0xA4A4)
    for i in range(0, len(out) - 2, 22):
        cp = (out[i] << 8) | out[i+1]
        if cp == 0xA4A4:
            print(f"\nGlyph 0xA4A4 (中):")
            for r in range(NEW_ROWS):
                row = (out[i+2+r*2] << 8) | out[i+2+r*2+1]
                line = "".join("##" if row & (1 << (15-c)) else ".." for c in range(16))
                print(f"  {line}")
            break

if __name__ == "__main__":
    main()
