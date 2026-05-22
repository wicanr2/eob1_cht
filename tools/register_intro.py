"""Register kEoB1IntroStrings* ZH_TWN providers in resources.cpp + add to eob1FloppyNeed."""
import re
from pathlib import Path

RES_CPP = Path(r"C:\Users\原來是個胖仔\scummvm_work\scummvm\devtools\create_kyradat\resources.cpp")
GAMES_CPP = Path(r"C:\Users\原來是個胖仔\scummvm_work\scummvm\devtools\create_kyradat\games.cpp")

NEW_PROVIDERS = [
    ("kEoB1IntroStringsTower",    "kEoB1IntroStringsTowerDOSChineseProvider"),
    ("kEoB1IntroStringsOrb",      "kEoB1IntroStringsOrbDOSChineseProvider"),
    ("kEoB1IntroStringsWdEntry",  "kEoB1IntroStringsWdEntryDOSChineseProvider"),
    ("kEoB1IntroStringsKing",     "kEoB1IntroStringsKingDOSChineseProvider"),
    ("kEoB1IntroStringsHands",    "kEoB1IntroStringsHandsDOSChineseProvider"),
    ("kEoB1IntroStringsWdExit",   "kEoB1IntroStringsWdExitDOSChineseProvider"),
    ("kEoB1IntroStringsTunnel",   "kEoB1IntroStringsTunnelDOSChineseProvider"),
]

# 1. Register in resources.cpp — insert after the existing intro chinese provider section, before MonsterDistAtt
text = RES_CPP.read_text(encoding="utf-8")
lines = text.split("\n")
out = []
added = False
for line in lines:
    out.append(line)
    # Insert after kEoB1NpcPresetsNamesDOSChineseProvider registration
    if not added and "kEoB1NpcPresetsNamesDOSChineseProvider }" in line:
        out.append("\t// Intro narration (Chinese fan translation)")
        for need_id, prov in NEW_PROVIDERS:
            out.append(f"\t{{ {need_id}, kEoB1, kPlatformDOS, kNoSpecial, ZH_TWN, &{prov} }},")
        added = True
RES_CPP.write_text("\n".join(out), encoding="utf-8")
print(f"Registered {len(NEW_PROVIDERS)} intro providers in resources.cpp" if added else "WARNING: could not find insertion point")

# 2. Add to eob1FloppyNeed[] in games.cpp
gtext = GAMES_CPP.read_text(encoding="utf-8")
# Find eob1FloppyNeed[] and add intro strings before the -1 terminator
new_needs = "\n\t".join([
    "// Intro narration (used by Chinese fan translation)",
    "kEoB1IntroStringsTower,",
    "kEoB1IntroStringsOrb,",
    "kEoB1IntroStringsWdEntry,",
    "kEoB1IntroStringsKing,",
    "kEoB1IntroStringsHands,",
    "kEoB1IntroStringsWdExit,",
    "kEoB1IntroStringsTunnel,",
    "",
])

marker = "const int eob1FloppyNeed[] = {"
end_marker = "-1\n};\n\nconst int eob1FloppyOldNeed[] = {"
i_start = gtext.find(marker)
if i_start == -1:
    print("WARNING: can't find eob1FloppyNeed")
else:
    i_end = gtext.find(end_marker, i_start)
    if i_end == -1:
        print("WARNING: can't find eob1FloppyNeed end")
    else:
        # Replace -1\n} with new entries + -1
        before = gtext[:i_end]
        after = gtext[i_end:]
        # Find the "\t-1" line — replace by new_needs + \t-1
        gtext = before.rstrip() + "\n\t" + new_needs + "\t-1\n};\n\nconst int eob1FloppyOldNeed[] = {"
        # Wait this is messed up. Let me just do it via regex.
        pass

# Cleaner: regex-replace the eob1FloppyNeed[] block to add new needs before -1
import re
m = re.search(r"(const int eob1FloppyNeed\[\] = \{.*?)(\t-1\s*\n\};)", gtext, re.DOTALL)
if m:
    body = m.group(1)
    end = m.group(2)
    # Check if already added
    if "kEoB1IntroStringsTower" in body:
        print("eob1FloppyNeed already has intro entries — skipping")
    else:
        addition = (
            "\n\t// Intro narration (used by Chinese fan translation)\n"
            "\tkEoB1IntroStringsTower,\n"
            "\tkEoB1IntroStringsOrb,\n"
            "\tkEoB1IntroStringsWdEntry,\n"
            "\tkEoB1IntroStringsKing,\n"
            "\tkEoB1IntroStringsHands,\n"
            "\tkEoB1IntroStringsWdExit,\n"
            "\tkEoB1IntroStringsTunnel,\n"
        )
        new_block = body + addition + "\n" + end
        gtext = gtext[:m.start()] + new_block + gtext[m.end():]
        GAMES_CPP.write_text(gtext, encoding="utf-8")
        print(f"Added {len(NEW_PROVIDERS)} intro entries to eob1FloppyNeed[]")
else:
    print("WARNING: regex didn't match eob1FloppyNeed")
