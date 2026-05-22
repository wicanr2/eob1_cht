"""Parse the kyra.dat PAK file and find INDEX version."""
import sys, struct
from pathlib import Path

p = Path(r"\\wsl$\Ubuntu-22.04\root\eob1cht\KYRA.DAT")
if not p.exists():
    print("Trying Windows-side copy via wsl")
    p = Path(r"C:\Temp\KYRA.DAT")
data = p.read_bytes()
print(f"File size: {len(data)}")

# PAK format: header [4-byte LE offset][null-terminated filename][... repeat ...][0][data]
# Actually: list of (filename, offset) tuples ending with a special marker

# Try parsing as: uint32 LE offset + asciiz filename until offset=0
pos = 0
files = []
first_offset = struct.unpack("<I", data[0:4])[0]
print(f"First offset: 0x{first_offset:X}")
i = 0
while True:
    offset = struct.unpack("<I", data[i:i+4])[0]
    i += 4
    if offset == 0:
        break
    name_start = i
    name_end = data.find(b'\0', name_start)
    name = data[name_start:name_end].decode('latin-1', errors='replace')
    i = name_end + 1
    files.append((name, offset))
    if i >= first_offset:
        break

print(f"\nFound {len(files)} files in PAK:")
for n, o in files[:20]:
    print(f"  0x{o:08X}  {n}")
if len(files) > 20:
    print(f"  ... and {len(files)-20} more")

# Find INDEX
for n, o in files:
    if n == "INDEX":
        # First 4 bytes = version (BE)
        ver_bytes = data[o:o+4]
        ver = struct.unpack(">I", ver_bytes)[0]
        print(f"\nINDEX file at offset 0x{o:X}, version = {ver}")
        # Then 4-byte includedGames count, then 2-byte entries (gameDef, lang)
        num_games = struct.unpack(">I", data[o+4:o+8])[0]
        print(f"includedGames = {num_games}")
        # Total size of INDEX file = 8 + 2*N
        expected_size = 8 + num_games * 2
        print(f"Expected INDEX file size: {expected_size} bytes")
        # Find next file's offset to compute actual size
        idx_in_list = next(i for i, f in enumerate(files) if f[0] == "INDEX")
        if idx_in_list + 1 < len(files):
            actual_size = files[idx_in_list+1][1] - o
            print(f"Actual INDEX size: {actual_size} bytes")
        # Print first 10 game entries
        for g in range(min(10, num_games)):
            entry = struct.unpack(">H", data[o+8+g*2:o+10+g*2])[0]
            game_id = (entry >> 12) & 0xF
            platform = (entry >> 8) & 0xF
            special = (entry >> 4) & 0xF
            lang = entry & 0xF
            print(f"  game={game_id} platform={platform} special={special} lang={lang}  (raw 0x{entry:04X})")
        break
else:
    print("\nNO INDEX FILE FOUND!")
