"""Scan CHINFONT.COD for actual Big5 codepoint runs (lead 0xA1-0xFE)."""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

data = Path(r"E:\dos1866\eob2\CHINFONT.COD").read_bytes()
print(f"Size: {len(data)}\n")

# Find runs of valid Big5 sequences (each 2 bytes; lead 0xA1-0xFE, trail valid)
def is_big5_lead(b):
    return 0xA1 <= b <= 0xFE

def is_big5_trail(b):
    return (0x40 <= b <= 0x7E) or (0xA1 <= b <= 0xFE)

i = 0
runs = []
while i + 1 < len(data):
    if is_big5_lead(data[i]) and is_big5_trail(data[i+1]):
        # Start of run
        start = i
        chars = []
        while i + 1 < len(data) and is_big5_lead(data[i]) and is_big5_trail(data[i+1]):
            cp = (data[i] << 8) | data[i+1]
            try:
                chars.append(bytes([cp >> 8, cp & 0xFF]).decode('cp950'))
            except:
                chars.append(f"[{cp:04X}]")
            i += 2
        runs.append((start, i, chars))
    else:
        i += 1

print(f"Found {len(runs)} Big5 runs")
print("\nFirst 20 runs:")
for off_start, off_end, chars in runs[:20]:
    txt = "".join(chars)[:40]
    print(f"  offset 0x{off_start:04X}-0x{off_end:04X} ({off_end-off_start:3} bytes): {txt}")

print("\nRuns of >= 6 chars:")
big_runs = [(s, e, c) for s, e, c in runs if (e-s) >= 12]
for s, e, c in big_runs[:30]:
    txt = "".join(c)
    print(f"  0x{s:04X}: {txt}")

# Now: hypothesis - immediately before each Big5 run, find the 5-byte code+count entry
print("\nLooking back 5 bytes before each Big5 run:")
for s, e, c in runs[:15]:
    if s >= 5:
        prefix = data[s-5:s]
        code = prefix[:4].decode('latin-1', errors='replace')
        count = prefix[4]
        actual_chars = (e-s) // 2
        print(f"  Code {code!r} count={count:3} actual_chars_after={actual_chars} chars={''.join(c)[:30]}")
