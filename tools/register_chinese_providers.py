"""Inject Chinese provider registrations into resources.cpp.

Finds all `{ ..., kEoB1, kPlatformDOS, ..., EN_ANY, &kEoB1XxxDOSEnglishProvider },`
lines and appends corresponding ZH_TWN entries right after them, plus inserts
`#include "resources/eob1_dos_chinese.h"` near the other Chinese includes.
"""
import re
from pathlib import Path

RES_CPP = Path(r"C:\Users\原來是個胖仔\scummvm_work\scummvm\devtools\create_kyradat\resources.cpp")

text = RES_CPP.read_text(encoding="utf-8")

# 0. Load list of providers that actually exist in our CHN header
CHN_HEADER = Path(r"C:\Users\原來是個胖仔\scummvm_work\scummvm\devtools\create_kyradat\resources\eob1_dos_chinese.h")
chn_text = CHN_HEADER.read_text(encoding="utf-8")
chn_providers = set()
for m in re.finditer(r"static const StringListProvider (kEoB1\w+DOSChineseProvider)", chn_text):
    chn_providers.add(m.group(1))
print(f"Found {len(chn_providers)} CHN providers in header")

# 1. Add include if missing
if '#include "resources/eob1_dos_chinese.h"' not in text:
    text = text.replace(
        '#include "resources/eob2_dos_chinese.h"',
        '#include "resources/eob1_dos_chinese.h"\n#include "resources/eob2_dos_chinese.h"',
        1
    )
    print("Added #include for eob1_dos_chinese.h")

# 2. Find and clone EOB1 EN_ANY entries
# Pattern: anything ending with EN_ANY, &kEoB1<something>DOSEnglishProvider },
# Skip already-registered entries
pat = re.compile(
    r"(\{\s*(\w+),\s*kEoB1,\s*kPlatformDOS,\s*(\w+),\s*EN_ANY,\s*&kEoB1(\w+)DOSEnglishProvider\s*\},?)"
)

inserted = 0
result_lines = []
for line in text.split("\n"):
    result_lines.append(line)
    m = pat.search(line)
    if m:
        full_entry = m.group(1)
        provider_id = m.group(2)
        special = m.group(3)
        name_suffix = m.group(4)
        chn_provider_name = f"kEoB1{name_suffix}DOSChineseProvider"
        # Only register if the CHN provider actually exists in our header
        if chn_provider_name not in chn_providers:
            continue
        chn_entry = f"\t{{ {provider_id}, kEoB1, kPlatformDOS, {special}, ZH_TWN, &{chn_provider_name} }},"
        # Avoid double-insertion
        if chn_provider_name not in text:
            result_lines.append(chn_entry)
            inserted += 1

if inserted:
    RES_CPP.write_text("\n".join(result_lines), encoding="utf-8")
    print(f"Inserted {inserted} ZH_TWN provider registrations")
else:
    print("No new registrations needed")
