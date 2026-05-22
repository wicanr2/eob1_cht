"""Show which strings in eob1_dos_chinese.h are still English (no translation found)."""
import re
from pathlib import Path

CHN_H = Path(r"C:\Users\原來是個胖仔\scummvm_work\scummvm\devtools\create_kyradat\resources\eob1_dos_chinese.h")
text = CHN_H.read_text(encoding="utf-8")

# Find all string literals — if no hex-escape and no /* */ comment after, it's untranslated
# Pattern: "literal text",   (no comment)
untranslated = []
cur_array = None
for line in text.split("\n"):
    if m := re.match(r"static const char \*const (kEoB1\w+DOSChinese)\[", line):
        cur_array = m.group(1)
        continue
    m = re.match(r'\s*"([^"]*)",?\s*(/\*.*\*/)?\s*$', line)
    if m:
        s = m.group(1)
        has_comment = m.group(2)
        # If string contains hex bytes, it's translated
        has_hex = '\\x' in s
        if not has_hex and not has_comment and s.strip() and not all(c in '%dsxbf0123456789 \\rn\t' for c in s):
            untranslated.append((cur_array, s))

print(f"Total untranslated: {len(untranslated)}")
print("\nBy array:")
from collections import defaultdict
by_array = defaultdict(list)
for arr, s in untranslated:
    by_array[arr].append(s)
for arr, ss in by_array.items():
    print(f"\n--- {arr} ({len(ss)} untranslated) ---")
    for s in ss:
        print(f"  {s!r}")
