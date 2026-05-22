"""Remove ZH_TWN provider registrations that reference providers not in our CHN header."""
import re
from pathlib import Path

RES_CPP = Path(r"C:\Users\原來是個胖仔\scummvm_work\scummvm\devtools\create_kyradat\resources.cpp")
CHN_HEADER = Path(r"C:\Users\原來是個胖仔\scummvm_work\scummvm\devtools\create_kyradat\resources\eob1_dos_chinese.h")

chn_providers = set()
for m in re.finditer(r"static const StringListProvider (kEoB1\w+DOSChineseProvider)", CHN_HEADER.read_text(encoding="utf-8")):
    chn_providers.add(m.group(1))

text = RES_CPP.read_text(encoding="utf-8")
out_lines = []
removed = 0
for line in text.split("\n"):
    m = re.search(r"&(kEoB1\w+DOSChineseProvider)", line)
    if m and m.group(1) not in chn_providers:
        removed += 1
        continue
    out_lines.append(line)

RES_CPP.write_text("\n".join(out_lines), encoding="utf-8")
print(f"Removed {removed} broken ZH_TWN registrations")
