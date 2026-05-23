"""Extract EN item names from EOB1 EOBDATA6.PAK / item.dat. Tolerant parser."""
import struct
from pathlib import Path

PAK = Path(r'D:\03_game_tmp\eob1_cht\win64-build\game\EOBDATA6.PAK')


def parse_pak_toc(data):
    """Westwood PAK: 4-byte LE offset + null-term name, repeating. End = offset==0."""
    entries = []
    pos = 0
    first_off = None
    while pos < len(data) - 4:
        # Need pos + 4 bytes for offset, then at least 1 byte for name
        offset = struct.unpack_from('<I', data, pos)[0]
        if offset == 0:
            break
        if offset > len(data):
            print(f"  bad offset {offset:x} at pos {pos:x}, stopping TOC")
            break
        if first_off is None:
            first_off = offset
        pos += 4
        # Read null-term name
        end = data.index(0, pos)
        name = data[pos:end].decode('ascii', errors='replace')
        pos = end + 1
        if not name:
            break
        entries.append((name, offset))
        # Stop when pos reaches first file's offset (end of TOC)
        if pos >= first_off:
            break
    # Compute sizes
    result = []
    for i, (n, o) in enumerate(entries):
        sz = (entries[i+1][1] if i+1 < len(entries) else len(data)) - o
        result.append((n, o, sz))
    return result


data = PAK.read_bytes()
entries = parse_pak_toc(data)
print(f"=== {PAK.name} ({len(data)} bytes, {len(entries)} entries) ===")
item_dat = None
for n, o, s in entries:
    is_item = n.lower() == 'item.dat'
    if is_item:
        item_dat = data[o:o+s]
        print(f"  *** {n} @ {o:08x} size={s}")

if item_dat is None:
    print("\nITEM.DAT not found.")
    exit(1)

print(f"\n=== Parsing ITEM.DAT ({len(item_dat)} bytes) ===")
# DOS = little-endian, EoBItem = 14 bytes (per items_eob.cpp:40-53)
num_items = struct.unpack('<H', item_dat[:2])[0]
print(f"numItems = {num_items}")
pos = 2 + num_items * 14
num_names = struct.unpack('<H', item_dat[pos:pos+2])[0]
pos += 2
print(f"numItemNames = {num_names}")

names = []
for i in range(num_names):
    raw = item_dat[pos:pos+35]
    nul = raw.find(0)
    s = raw[:nul if nul >= 0 else 35].decode('ascii', errors='replace').strip()
    names.append(s)
    pos += 35

print(f"\n=== {len(names)} item names ===")
for i, n in enumerate(names):
    print(f"  [{i:3d}] {n!r}")

# Write C array
out = Path(r'D:\03_game_tmp\eob1_cht\tools\item_names_extracted.txt')
with open(out, 'w', encoding='utf-8') as f:
    f.write(f"// {len(names)} item names extracted from EOB1 DOS EN PAK (EOBDATA6.PAK/ITEM.DAT)\n")
    f.write(f"static const char *const kEoB1ItemNamesDOSEnglish[{len(names)}] = {{\n")
    for n in names:
        esc = n.replace('\\', '\\\\').replace('"', '\\"')
        f.write(f'\t"{esc}",\n')
    f.write("};\n")
print(f"\nWrote {out}")
