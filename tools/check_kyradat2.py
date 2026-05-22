"""Find EOB1/ZH_TWN in INDEX."""
import struct
from pathlib import Path

p = Path(r"C:\Temp\KYRA.DAT")
data = p.read_bytes()

# Find INDEX by re-parsing
pos = 0
files = []
first_offset = struct.unpack("<I", data[0:4])[0]
i = 0
while i < first_offset:
    offset = struct.unpack("<I", data[i:i+4])[0]
    i += 4
    if offset == 0:
        break
    name_start = i
    name_end = data.find(b'\0', name_start)
    name = data[name_start:name_end].decode('latin-1', errors='replace')
    i = name_end + 1
    files.append((name, offset))

idx_file = next(f for f in files if f[0] == "INDEX")
o = idx_file[1]
version = struct.unpack(">I", data[o:o+4])[0]
num = struct.unpack(">I", data[o+4:o+8])[0]
print(f"INDEX: version={version}, includedGames={num}")
print(f"\nAll game definitions:")
target_eob1_zhtw = (3 << 12) | (0 << 8) | (0 << 4) | 10
print(f"\nLooking for EOB1 ZH_TWN = 0x{target_eob1_zhtw:04X} = {target_eob1_zhtw}")

found = False
for g in range(num):
    entry = struct.unpack(">H", data[o+8+g*2:o+10+g*2])[0]
    game = (entry >> 12) & 0xF
    plat = (entry >> 8) & 0xF
    spec = (entry >> 4) & 0xF
    lang = entry & 0xF
    marker = ""
    if entry == target_eob1_zhtw:
        marker = "  *** FOUND ***"
        found = True
    if game == 3:  # EOB1
        print(f"  EOB1: 0x{entry:04X}  game={game} plat={plat} spec={spec} lang={lang}{marker}")
    if game == 4:  # EOB2
        if lang == 10:
            print(f"  EOB2 ZH_TWN: 0x{entry:04X}  (for comparison)")
print(f"\nFound EOB1 ZH_TWN: {found}")
