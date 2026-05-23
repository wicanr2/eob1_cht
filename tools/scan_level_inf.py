"""Scan LEVEL*.INF files for ASCII string content. Run from WSL python3.

EOB1 has 12 levels split across PAKs:
- EOBDATA3.PAK: LEVEL1-3.INF
- EOBDATA4.PAK: LEVEL4-6.INF (probably)
- EOBDATA5.PAK: LEVEL10-12.INF
- EOBDATA6.PAK: LEVEL7-9.INF

Extract LEVEL*.INF files and dump ASCII text runs >= 8 chars
to identify action messages embedded in level scripts.
"""
import struct, re
from pathlib import Path

GAME = Path('/mnt/d/03_game_tmp/eob1_cht/win64-build/game')
PAKS = ['EOBDATA3.PAK', 'EOBDATA4.PAK', 'EOBDATA5.PAK', 'EOBDATA6.PAK']

OUT_DIR = Path('/mnt/d/03_game_tmp/eob1_cht/tools/level_inf_dump')
OUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_pak(data):
    entries = []
    pos = 0
    first = None
    while pos < len(data) - 4:
        o = struct.unpack_from('<I', data, pos)[0]
        if o == 0 or o > len(data):
            break
        if first is None:
            first = o
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
        if pos >= first:
            break
    return [
        (n, o, (entries[i+1][1] if i+1 < len(entries) else len(data)) - o)
        for i, (n, o) in enumerate(entries)
    ]


all_levels = {}
for pak_name in PAKS:
    pak = GAME / pak_name
    if not pak.exists():
        continue
    data = pak.read_bytes()
    entries = parse_pak(data)
    for n, o, s in entries:
        if n.upper().startswith('LEVEL') and n.upper().endswith('.INF'):
            content = data[o:o+s]
            (OUT_DIR / n).write_bytes(content)
            all_levels[n] = content
            print(f"  Extracted {n} from {pak_name}: {s} bytes")

print(f"\nFound {len(all_levels)} LEVEL.INF files")

# Extract ASCII string runs from each
print(f"\n=== ASCII string runs (>= 8 chars, printable+\\r\\n) ===\n")
total_strings = 0
total_bytes = 0
all_strings = []
for name in sorted(all_levels):
    content = all_levels[name]
    # Find runs of printable ASCII (0x20-0x7E plus \r \n) at least 8 chars long
    matches = re.findall(rb'[\x20-\x7e\r\n]{8,}', content)
    print(f"--- {name} ({len(content)} bytes, {len(matches)} runs) ---")
    for m in matches:
        try:
            s = m.decode('ascii')
            # Skip pure-whitespace runs
            if not s.strip():
                continue
            # Skip filenames (e.g. BRICK1.CPS, .EGA, .CMP common suffix)
            if any(s.endswith(ext) for ext in ['.CPS', '.EGA', '.CMP', '.DAT', '.MAZ', '.INF', '.PAL', '.VCN', '.VMP', '.ECN', '.EMP']):
                continue
            # Found probable game text
            print(f"  [{len(s):4d}B] {s!r}")
            total_strings += 1
            total_bytes += len(s)
            all_strings.append((name, s))
        except UnicodeDecodeError:
            pass
    print()

print(f"\n=== TOTAL: {total_strings} strings, {total_bytes} bytes across {len(all_levels)} LEVEL.INF files ===")

# Save dump
import json
dump_path = OUT_DIR / 'all_strings.json'
dump_path.write_text(json.dumps(all_strings, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"Saved structured dump to {dump_path}")
