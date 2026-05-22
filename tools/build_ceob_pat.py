"""Convert EOB2 CHINFONT.FNT → ceob.pat (ScummVM Big5Font::loadPrefixedRaw format).

Input format (30 bytes per glyph):
  [0..1] cp_lo, cp_hi (Big5 codepoint LE)
  [2..29] 28 bytes XOR-encrypted (key alternates lo, hi)
          → decrypts to 14 rows × 2 bytes = 16x14 bitmap

Output format (per Big5Font::loadPrefixedRaw in scummvm/graphics/big5.cpp):
  [0..1] uint16 BE codepoint (high bit must be 1 — true for all Big5 leads 0xA1-0xFE)
  [2..29] 28 bytes raw bitmap (same row layout: 2 bytes per row × 14 rows)
  ... then 0xFFFF terminator

Usage:
  python build_ceob_pat.py E:/dos1866/eob2/CHINFONT.FNT ceob.pat
"""
import sys, struct
from pathlib import Path

GLYPH_BYTES = 30
ROWS = 14

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    src_path, dst_path = sys.argv[1], sys.argv[2]
    data = Path(src_path).read_bytes()
    assert len(data) % GLYPH_BYTES == 0, f"file size {len(data)} not multiple of {GLYPH_BYTES}"
    n = len(data) // GLYPH_BYTES
    out = bytearray()
    seen = set()
    skipped_dups = 0
    skipped_no_high = 0
    written = 0
    for i in range(n):
        block = data[i*GLYPH_BYTES:(i+1)*GLYPH_BYTES]
        lo, hi = block[0], block[1]
        cp = (hi << 8) | lo  # standard BE Big5 codepoint
        if not (cp & 0x8000):
            # ScummVM's loadPrefixedRaw skips entries without high bit
            skipped_no_high += 1
            continue
        if cp in seen:
            skipped_dups += 1
            continue
        seen.add(cp)
        enc = block[2:]
        dec = bytearray(28)
        for k in range(28):
            dec[k] = enc[k] ^ (lo if k % 2 == 0 else hi)
        # Write BE codepoint + 28-byte bitmap
        out += struct.pack(">H", cp)
        out += bytes(dec)
        written += 1
    # Terminator
    out += b"\xff\xff"
    Path(dst_path).write_bytes(out)
    print(f"Read {n} entries from {src_path}")
    print(f"Wrote {written} glyphs (skipped {skipped_dups} dups, {skipped_no_high} no-high-bit)")
    print(f"Output: {dst_path} ({len(out)} bytes)")
    # Quick sanity dump
    print(f"First 3 glyphs:")
    for i in range(3):
        base = i * 30
        cp = (out[base] << 8) | out[base+1]
        print(f"  cp=0x{cp:04X}  first row bytes: {out[base+2]:02X} {out[base+3]:02X}")

if __name__ == "__main__":
    main()
