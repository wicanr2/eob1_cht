"""Verify 憶 (0xBED0) is in the new ceob.pat."""
from pathlib import Path
data = Path(r"C:\Users\原來是個胖仔\scummvm_work\ceob.pat").read_bytes()
i = 0
found = False
while i + 26 <= len(data):
    cp = (data[i] << 8) | data[i+1]
    if cp == 0xFFFF:
        break
    if cp == 0xBED0:
        found = True
        print(f"憶 (0xBED0) at offset {i}, bitmap:")
        for r in range(12):
            row = (data[i+2+r*2] << 8) | data[i+2+r*2+1]
            line = "".join("##" if row & (1 << (15-c)) else ".." for c in range(16))
            print(f"  {line}")
        break
    i += 26  # 2 + 2*12 = 26 bytes per entry
if not found:
    print("NOT FOUND!")
