"""Parse create_kyradat.h enum to find what value 318 is."""
import re
from pathlib import Path

p = Path(r"C:\Users\原來是個胖仔\scummvm_work\scummvm\devtools\create_kyradat\create_kyradat.h")
text = p.read_text(encoding="utf-8")

# Find first enum
in_enum = False
val = -1
for line in text.split("\n"):
    if "enum kExtractID" in line:
        in_enum = True
        val = -1
        continue
    if in_enum:
        # End of enum
        if line.strip().startswith("};"):
            break
        # Strip comments
        line_clean = re.sub(r"//.*", "", line)
        line_clean = re.sub(r"/\*.*?\*/", "", line_clean)
        m = re.match(r"\s*(k\w+)\s*,?\s*$", line_clean)
        if m:
            val += 1
            if val == 318:
                print(f"Enum value 318 = {m.group(1)}")
                break
            # Print near vicinity
            if 315 <= val <= 322:
                print(f"  {val}: {m.group(1)}")
        # Handle explicit = NNN
        m = re.match(r"\s*(k\w+)\s*=\s*(\d+)\s*,?\s*$", line_clean)
        if m:
            val = int(m.group(2))
            if val == 318:
                print(f"Enum value 318 (explicit) = {m.group(1)}")
                break
