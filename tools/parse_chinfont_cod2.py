"""Better parser for CHINFONT.COD — counts are the entries but Big5 data location unknown."""
import sys, struct
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

data = Path(r"E:\dos1866\eob2\CHINFONT.COD").read_bytes()
print(f"File size: {len(data)}")
print()

# Try: each entry = 4-byte code + 1-byte count; total entries = N
# Then trailing block = sum(counts) * 2 bytes of Big5
# So size = 5*N + 2*total_chars

# Try N=??? by scanning forward as long as bytes 0-3 are printable ASCII
N = 0
total_chars = 0
codes = []
i = 0
while i + 5 <= len(data):
    code_bytes = data[i:i+4]
    # All 4 must be printable ASCII (0x20-0x7E) or '*'
    if not all(0x20 <= b <= 0x7E for b in code_bytes):
        break
    count = data[i+4]
    if count == 0 or count > 200:  # sanity
        break
    codes.append((code_bytes.decode('latin-1'), count, i))
    total_chars += count
    N += 1
    i += 5

print(f"Read {N} codes ending at offset {i}, total_chars = {total_chars}")
print(f"Expected data block: {N*5} + {total_chars*2} = {N*5 + total_chars*2}")
print(f"Actual file size:    {len(data)}")
print()

# Show last 10 codes
print("Last 10 codes:")
for c, n, off in codes[-10:]:
    print(f"  off={off:4} code={c!r} count={n}")

# Big5 block starts at offset i
print(f"\nBig5 data at offset {i} ({len(data)-i} bytes = {(len(data)-i)//2} Big5 chars)")
print(f"First 32 bytes of Big5 block hex: {data[i:i+32].hex()}")

# Parse Big5 chars in order
big5_chars = []
j = i
while j + 2 <= len(data):
    cp = (data[j] << 8) | data[j+1]
    big5_chars.append(cp)
    j += 2
print(f"Total Big5 chars in trailing block: {len(big5_chars)}")
print()

# Try to assign to codes
print("First 20 codes with chars:")
idx = 0
for c, n, _ in codes[:20]:
    cps = big5_chars[idx:idx+n]
    idx += n
    chars = []
    for cp in cps:
        try:
            chars.append(bytes([cp >> 8, cp & 0xFF]).decode('cp950'))
        except:
            chars.append(f'[{cp:04X}]')
    print(f"  {c!r:8} (n={n:3}): {''.join(chars)}")

# Try known codes
print("\nFinding canonical Zhuyin codes:")
idx = 0
char_idx_for_code = {}
for c, n, _ in codes:
    char_idx_for_code[c] = (idx, n)
    idx += n

for target in ['1***', '187*', '18**', '186*', '7***', 'u8**', 'WK7*', 'jk4*']:
    if target in char_idx_for_code:
        i0, n = char_idx_for_code[target]
        cps = big5_chars[i0:i0+n]
        chars = []
        for cp in cps:
            try: chars.append(bytes([cp >> 8, cp & 0xFF]).decode('cp950'))
            except: chars.append(f'[{cp:04X}]')
        print(f"  {target!r}: {''.join(chars)}")
    else:
        print(f"  {target!r}: code not found")
