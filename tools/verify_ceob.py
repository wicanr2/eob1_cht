"""Verify ceob.pat by rendering known Big5 glyphs."""
import sys
with open("ceob.pat", "rb") as f:
    data = f.read()
target = [0xA440, 0xA4A4, 0xA4E5, 0xA8EA]  # 一, 中, 圭, 樂
# Try also: 0xA440 first char "一"
found = {}
i = 0
while i + 30 <= len(data):
    cp = (data[i] << 8) | data[i+1]
    if cp == 0xFFFF: break
    if cp in target:
        found[cp] = data[i+2:i+30]
    i += 30

print(f"Found {len(found)}/{len(target)} target glyphs")
for cp, bm in found.items():
    print(f"\nGlyph 0x{cp:04X}:")
    for r in range(14):
        row = (bm[r*2] << 8) | bm[r*2+1]
        line = "".join("##" if row & (1 << (15-c)) else ".." for c in range(16))
        print(f"  {line}")
