"""Find what file in EOBDATA3.PAK contains the parchment text at offset 0x37e00."""
import struct
from pathlib import Path

PAK = Path(r'D:\03_game_tmp\eob1_cht\win64-build\game\EOBDATA3.PAK')
data = PAK.read_bytes()

# Iterate TOC tolerantly: read 4-byte offset + null-term name, until name is empty or offset hits first
entries = []
pos = 0
first_off = None
while pos < len(data) - 4:
    o = struct.unpack_from('<I', data, pos)[0]
    if o == 0:
        break
    if o > len(data):
        # might be end of TOC if pos is near first offset
        break
    if first_off is None:
        first_off = o
    pos += 4
    try:
        end = data.index(0, pos)
    except ValueError:
        break
    name = data[pos:end].decode('ascii', errors='replace')
    pos = end + 1
    if not name:
        break
    entries.append((name, o))
    if pos >= first_off:
        break

print(f"Parsed {len(entries)} entries from EOBDATA3.PAK TOC")
# Find file containing offset 0x37e00
target = 0x37e00
for i, (n, o) in enumerate(entries):
    next_o = entries[i+1][1] if i+1 < len(entries) else len(data)
    if o <= target < next_o:
        print(f"\nFile containing 0x{target:x}: {n}")
        print(f"  Starts at 0x{o:x}, size {next_o - o}")
        print(f"  Offset within file: 0x{target - o:x}")
        break

# Also list all files with .DAT or .CPS or .INF
print(f"\nAll files in EOBDATA3.PAK (size > 100 bytes):")
for i, (n, o) in enumerate(entries):
    sz = (entries[i+1][1] if i+1 < len(entries) else len(data)) - o
    if sz > 100:
        print(f"  {n:20s} @ {o:08x} size={sz}")
