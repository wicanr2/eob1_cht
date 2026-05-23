"""List contents of all EOB1 PAK files."""
import struct
from pathlib import Path

GAME_DIR = Path(r'D:\03_game_tmp\eob1_cht\win64-build\game')
PAKS = ['EOBDATA1.PAK', 'EOBDATA2.PAK', 'EOBDATA3.PAK', 'EOBDATA4.PAK',
        'EOBDATA5.PAK', 'EOBDATA6.PAK', 'EYE.PAK']


def read_cstring(data, offset, max_len=64):
    end = offset
    while end < len(data) and end - offset < max_len and data[end] != 0:
        end += 1
    return data[offset:end], end + 1


def parse_pak(name, data):
    print(f"\n=== {name} ({len(data)} bytes) ===")
    # Try LE first
    try:
        pos = 0
        entries = []
        first_offset = None
        while pos < len(data):
            offset = struct.unpack_from('<I', data, pos)[0]
            pos += 4
            if offset == 0:
                break
            if first_offset is None:
                first_offset = offset
            if offset > len(data):
                raise ValueError(f"offset {offset:x} > size {len(data):x}")
            name_raw, pos = read_cstring(data, pos)
            try:
                fname = name_raw.decode('ascii')
            except UnicodeDecodeError:
                raise ValueError(f"non-ASCII filename at pos {pos:x}")
            if not fname:
                break
            entries.append((fname, offset))
            if pos >= first_offset:
                break
        # compute sizes
        for i, (fn, off) in enumerate(entries):
            sz = (entries[i + 1][1] if i + 1 < len(entries) else len(data)) - off
            mark = '  <-- item.dat!' if fn.lower() == 'item.dat' else ''
            print(f"  {fn:20s} @ {off:08x} size={sz}{mark}")
    except Exception as e:
        # First 32 bytes hex
        hex_str = ' '.join(f'{b:02x}' for b in data[:32])
        print(f"  parse FAIL: {e}")
        print(f"  first 32 bytes: {hex_str}")


for pak in PAKS:
    p = GAME_DIR / pak
    if not p.exists():
        print(f"{pak}: missing")
        continue
    parse_pak(pak, p.read_bytes())
