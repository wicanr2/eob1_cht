"""Extract TEXT.DAT from EOBDATA3.PAK and dump string table."""
import struct
from pathlib import Path

PAK = Path(r'D:\03_game_tmp\eob1_cht\win64-build\game\EOBDATA3.PAK')
data = PAK.read_bytes()

# TEXT.DAT location (per find_text_dat.py)
TEXT_OFF = 0x348fc
TEXT_SIZE = 16105
text_dat = data[TEXT_OFF:TEXT_OFF + TEXT_SIZE]

out = Path(r'D:\03_game_tmp\eob1_cht\tools\TEXT_dat.bin')
out.write_bytes(text_dat)
print(f"Extracted TEXT.DAT to {out} ({len(text_dat)} bytes)")

# Parse offset table
# Per text_rpg.cpp: str = page5 + LE_u16(page5[(stringId-1) * 2])
# So bytes[0..2] = offset of string 1, etc.
# Offset table ends where first offset points to.

offsets = []
for k in range(200):  # try up to 200 entries
    pos = k * 2
    if pos + 2 > len(text_dat):
        break
    o = struct.unpack('<H', text_dat[pos:pos+2])[0]
    if o == 0:
        break
    if k == 0:
        if o < 4 or o > 2000:
            break
    if offsets and (o <= offsets[-1] or o >= len(text_dat)):
        break
    offsets.append(o)
    # Stop when next read would be past first string
    if pos + 2 >= offsets[0]:
        break

print(f"Detected {len(offsets)} string offsets")

print(f"\n=== Strings ({len(offsets)} entries) ===")
for i, o in enumerate(offsets):
    end = text_dat.find(0, o)
    if end < 0:
        end = len(text_dat)
    s = text_dat[o:end].decode('ascii', errors='replace')
    # Truncate display
    preview = s if len(s) < 200 else s[:200] + '...'
    print(f"\n[{i+1}] @ {o:04x} ({end-o} bytes):")
    print(f"  {preview!r}")
