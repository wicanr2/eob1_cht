"""Parse EOB2's CHINFONT.COD — looks like Zhuyin (Bopomofo) IME dictionary.

Format:
  [4 bytes ASCII Zhuyin code, '*' padded]
  [1 byte count N]
  [N * 2 bytes Big5 codepoint candidates, LE or BE TBD]

Zhuyin keyboard layout (standard PC layout):
  Row 1: 1=ㄅ 2=ㄉ 3=ˇ 4=ˋ 5=ㄓ 6=ˊ 7=˙ 8=ㄚ 9=ㄞ 0=ㄢ -=ㄦ
  Row q: q=ㄆ w=ㄊ e=ㄍ r=ㄐ t=ㄔ y=ㄗ u=ㄧ i=ㄛ o=ㄟ p=ㄣ
  Row a: a=ㄇ s=ㄋ d=ㄎ f=ㄑ g=ㄕ h=ㄘ j=ㄨ k=ㄜ l=ㄠ ;=ㄤ
  Row z: z=ㄈ x=ㄌ c=ㄏ v=ㄒ b=ㄖ n=ㄙ m=ㄩ ,=ㄝ .=ㄡ /=ㄥ
"""
from pathlib import Path

ZHUYIN = {
    '1': 'ㄅ', '2': 'ㄉ', '3': 'ˇ', '4': 'ˋ', '5': 'ㄓ', '6': 'ˊ', '7': '˙',
    '8': 'ㄚ', '9': 'ㄞ', '0': 'ㄢ', '-': 'ㄦ',
    'q': 'ㄆ', 'w': 'ㄊ', 'e': 'ㄍ', 'r': 'ㄐ', 't': 'ㄔ', 'y': 'ㄗ',
    'u': 'ㄧ', 'i': 'ㄛ', 'o': 'ㄟ', 'p': 'ㄣ',
    'a': 'ㄇ', 's': 'ㄋ', 'd': 'ㄎ', 'f': 'ㄑ', 'g': 'ㄕ', 'h': 'ㄘ',
    'j': 'ㄨ', 'k': 'ㄜ', 'l': 'ㄠ', ';': 'ㄤ',
    'z': 'ㄈ', 'x': 'ㄌ', 'c': 'ㄏ', 'v': 'ㄒ', 'b': 'ㄖ', 'n': 'ㄙ',
    'm': 'ㄩ', ',': 'ㄝ', '.': 'ㄡ', '/': 'ㄥ',
    'A': 'ㄇ', 'B': 'ㄖ', 'C': 'ㄏ', 'D': 'ㄎ', 'E': 'ㄍ', 'F': 'ㄑ',
    'G': 'ㄕ', 'H': 'ㄘ', 'I': 'ㄛ', 'J': 'ㄨ', 'K': 'ㄜ', 'L': 'ㄠ',
    'M': 'ㄩ', 'N': 'ㄙ', 'O': 'ㄟ', 'P': 'ㄣ', 'Q': 'ㄆ', 'R': 'ㄐ',
    'S': 'ㄋ', 'T': 'ㄔ', 'U': 'ㄧ', 'V': 'ㄒ', 'W': 'ㄊ', 'X': 'ㄌ',
    'Y': 'ㄗ', 'Z': 'ㄈ',
    '*': '_',  # placeholder marker
}

def decode_zhuyin(code):
    return "".join(ZHUYIN.get(c, '?') for c in code)

import sys
sys.stdout.reconfigure(encoding='utf-8')
data = Path(r"E:\dos1866\eob2\CHINFONT.COD").read_bytes()
print(f"File size: {len(data)}")

i = 0
entries = []
errors = 0
while i < len(data):
    if i + 5 > len(data):
        break
    code = data[i:i+4].decode('latin-1', errors='replace')
    count = data[i+4]
    i += 5
    if i + count*2 > len(data):
        # Last record might be truncated
        print(f"Truncated at offset {i-5}, code={code!r}, count={count}")
        break
    cps = []
    for _ in range(count):
        b1, b2 = data[i], data[i+1]
        i += 2
        # Try BE first
        cp = (b1 << 8) | b2
        cps.append(cp)
    entries.append((code, count, cps))

print(f"Parsed {len(entries)} entries, {sum(e[1] for e in entries)} total Big5 chars")

# Show first 30 entries with decoded Zhuyin + Big5 chars
print("\nFirst 30 entries:")
for code, count, cps in entries[:30]:
    chars_be = []
    for cp in cps:
        try:
            chars_be.append(bytes([cp >> 8, cp & 0xFF]).decode('cp950'))
        except:
            chars_be.append('?')
    chars_le = []
    for cp in cps:
        try:
            chars_le.append(bytes([cp & 0xFF, cp >> 8]).decode('cp950'))
        except:
            chars_le.append('?')
    print(f"  {code!r:8} ({decode_zhuyin(code):4}) count={count:2} BE: {''.join(chars_be)}  LE: {''.join(chars_le)}")

# Test specific codes: 1*** (ㄅ_), 187* (ㄅㄚ˙), 18** (ㄅㄚ_)
print("\nLooking for canonical Zhuyin codes:")
known_codes = [b'1***', b'187*', b'18**', b'186*', b'7***', b'u8**']
for k in known_codes:
    found = [(c,n,cps) for c,n,cps in entries if c.encode('latin-1') == k]
    if found:
        c, n, cps = found[0]
        chars = []
        for cp in cps:
            try: chars.append(bytes([cp >> 8, cp & 0xFF]).decode('cp950'))
            except: chars.append('?')
        print(f"  {k!r} ({decode_zhuyin(c)}): {''.join(chars)}")
    else:
        print(f"  {k!r}: not found")
