"""Build ceob.pat using BoutiqueBitmap9x9 TTF at 9x9 (vs the original 16x14).

Output format (ScummVM Big5Font::loadPrefixedRaw with height=9):
  Repeating: [BE uint16 Big5 codepoint][9 rows * 2 bytes bitmap] (high bit must be set)
  Terminated by 0xFFFF.

The glyph bitmap is 16 columns wide (per kChineseTraditionalWidth=16) × 9 rows tall.
BoutiqueBitmap9x9 chars are ~9 wide; we left-align in the 16-col slot.
"""
import sys, struct, os, shutil
from pathlib import Path

TTF_ORIG = r"C:\Users\原來是個胖仔\eob_analysis\BoutiqueBitmap9x9.ttf"
TTF_ASCII_COPY = r"C:\Temp\Boutique.ttf"
OUT_PATH = r"C:\Users\原來是個胖仔\scummvm_work\ceob.pat"

# Ensure ASCII path for freetype-py
if not os.path.exists(TTF_ASCII_COPY) or os.path.getmtime(TTF_ORIG) > os.path.getmtime(TTF_ASCII_COPY):
    shutil.copy(TTF_ORIG, TTF_ASCII_COPY)

import freetype

HEIGHT = 9
WIDTH = 16  # forced by Big5Font::kChineseTraditionalWidth

def render_glyph(face, big5_cp):
    """Big5 codepoint -> 16x9 bitmap (18 bytes, 2 bytes per row)."""
    hi, lo = big5_cp >> 8, big5_cp & 0xFF
    try:
        unicode_char = bytes([hi, lo]).decode("cp950")
    except Exception:
        return None
    try:
        face.load_char(
            unicode_char,
            freetype.FT_LOAD_RENDER | freetype.FT_LOAD_MONOCHROME | freetype.FT_LOAD_TARGET_MONO
        )
    except Exception:
        return None
    bmp = face.glyph.bitmap
    w, h, pitch = bmp.width, bmp.rows, bmp.pitch
    if w == 0 or h == 0:
        # Empty glyph (e.g., space) — emit zeros
        return bytes(2 * HEIGHT)

    out = bytearray(2 * HEIGHT)
    # Top-align (rows 0..min(h, HEIGHT))
    for r in range(min(h, HEIGHT)):
        # FreeType row is `pitch` bytes wide; MSB-first within each byte
        for c in range(min(w, WIDTH)):
            src_byte = bmp.buffer[r * pitch + c // 8]
            if src_byte & (0x80 >> (c % 8)):
                out[r * 2 + c // 8] |= (0x80 >> (c % 8))
    return bytes(out)

def main():
    face = freetype.Face(TTF_ASCII_COPY)
    face.set_pixel_sizes(HEIGHT, HEIGHT)
    print(f"Face loaded; rendering at {HEIGHT}px")

    # Iterate all Big5 codepoints (lead 0xA1..0xFE, trail 0x40..0x7E + 0xA1..0xFE)
    out = bytearray()
    written = 0
    skipped = 0
    for lead in range(0xA1, 0xFF):
        trails = list(range(0x40, 0x7F)) + list(range(0xA1, 0xFF))
        for trail in trails:
            cp = (lead << 8) | trail
            glyph = render_glyph(face, cp)
            if glyph is None:
                skipped += 1
                continue
            # All-zero glyphs: skip (saves space; engine returns "no glyph" anyway)
            if not any(glyph):
                skipped += 1
                continue
            out += struct.pack(">H", cp)
            out += glyph
            written += 1

    out += b"\xff\xff"
    Path(OUT_PATH).write_bytes(out)
    print(f"Wrote {OUT_PATH}: {written} glyphs ({len(out)} bytes), skipped {skipped}")

if __name__ == "__main__":
    main()
