"""Build ceob.pat with hybrid font:
  - Primary: EOB2 CHINFONT.FNT cropped to 16x12 (rows 1..13)
  - Fallback: BoutiqueBitmap9x9 rendered at 12px for codepoints EOB2 lacks

Output: prefixed-raw format with height=12 for Big5Font::loadPrefixedRaw.
"""
import os, sys, struct, shutil
from pathlib import Path

EOB2_FONT = r"E:\dos1866\eob2\CHINFONT.FNT"
TTF_ORIG = r"C:\Users\原來是個胖仔\eob_analysis\BoutiqueBitmap9x9.ttf"
TTF_ASCII = r"C:\Temp\Boutique.ttf"
DST_PATH = r"C:\Users\原來是個胖仔\scummvm_work\ceob.pat"

HEIGHT = 12
WIDTH = 16
TOP_TRIM = 1   # for EOB2 14-row crop

def load_eob2_font():
    data = Path(EOB2_FONT).read_bytes()
    assert len(data) % 30 == 0
    glyphs = {}
    for i in range(len(data) // 30):
        b = data[i*30:(i+1)*30]
        lo, hi = b[0], b[1]
        cp = (hi << 8) | lo
        if not (cp & 0x8000):
            continue
        if cp in glyphs:
            continue
        enc = b[2:]
        dec = bytearray(28)
        for k in range(28):
            dec[k] = enc[k] ^ (lo if k % 2 == 0 else hi)
        # Crop to 12 rows [TOP_TRIM .. TOP_TRIM+HEIGHT)
        cropped = bytearray()
        for r in range(TOP_TRIM, TOP_TRIM + HEIGHT):
            cropped += dec[r*2:r*2+2]
        glyphs[cp] = bytes(cropped)
    return glyphs

def render_boutique(cp, face):
    hi, lo = cp >> 8, cp & 0xFF
    try:
        ch = bytes([hi, lo]).decode("cp950")
    except Exception:
        return None
    try:
        import freetype
        face.load_char(
            ch,
            freetype.FT_LOAD_RENDER | freetype.FT_LOAD_MONOCHROME | freetype.FT_LOAD_TARGET_MONO
        )
    except Exception:
        return None
    bmp = face.glyph.bitmap
    w, hh, pitch = bmp.width, bmp.rows, bmp.pitch
    if w == 0 or hh == 0:
        return None
    out = bytearray(2 * HEIGHT)
    # Top-align with 1-row margin (so it sits visually similar to EOB2 chars)
    y_offset = max(0, (HEIGHT - hh) // 2)
    x_offset = max(0, (WIDTH - w) // 2 - 1)
    for r in range(min(hh, HEIGHT - y_offset)):
        dst_r = r + y_offset
        for c in range(min(w, WIDTH - x_offset)):
            dst_c = c + x_offset
            src_byte = bmp.buffer[r * pitch + c // 8]
            if src_byte & (0x80 >> (c % 8)):
                out[dst_r * 2 + dst_c // 8] |= (0x80 >> (dst_c % 8))
    if not any(out):
        return None
    return bytes(out)

def main():
    eob2 = load_eob2_font()
    print(f"EOB2 font: {len(eob2)} glyphs")

    # Prepare freetype for fallback
    if not os.path.exists(TTF_ASCII) or os.path.getmtime(TTF_ORIG) > os.path.getmtime(TTF_ASCII):
        shutil.copy(TTF_ORIG, TTF_ASCII)
    import freetype
    face = freetype.Face(TTF_ASCII)
    face.set_pixel_sizes(HEIGHT, HEIGHT)
    print("Boutique fallback loaded at 12px")

    out = bytearray()
    written_eob2 = 0
    written_boutique = 0
    skipped = 0

    # Iterate ALL Big5 codepoints (lead 0xA1-0xFE, trail 0x40-0x7E and 0xA1-0xFE)
    for lead in range(0xA1, 0xFF):
        for trail in list(range(0x40, 0x7F)) + list(range(0xA1, 0xFF)):
            cp = (lead << 8) | trail
            glyph = eob2.get(cp)
            if glyph is not None:
                out += struct.pack(">H", cp)
                out += glyph
                written_eob2 += 1
            else:
                # Try Boutique fallback
                fb = render_boutique(cp, face)
                if fb is not None:
                    out += struct.pack(">H", cp)
                    out += fb
                    written_boutique += 1
                else:
                    skipped += 1
    out += b"\xff\xff"
    Path(DST_PATH).write_bytes(out)
    total = written_eob2 + written_boutique
    print(f"Wrote {DST_PATH}: {total} glyphs ({len(out)} bytes)")
    print(f"  From EOB2:       {written_eob2}")
    print(f"  From Boutique:   {written_boutique}")
    print(f"  Skipped (no cp): {skipped}")

    # Verify 憶 (0xBE56)
    YI_CP = 0xBE56
    print(f"\nVerify 憶 (0x{YI_CP:04X}):")
    print(f"  In EOB2: {YI_CP in eob2}")
    fb = render_boutique(YI_CP, face)
    print(f"  Boutique can render: {fb is not None}")

if __name__ == "__main__":
    main()
