"""Add intro string ids to eob1FloppyNeed[] — careful version."""
import re
from pathlib import Path

GAMES_CPP = Path(r"C:\Users\原來是個胖仔\scummvm_work\scummvm\devtools\create_kyradat\games.cpp")
text = GAMES_CPP.read_text(encoding="utf-8")

# Find eob1FloppyNeed start
i = text.find("const int eob1FloppyNeed[] = {")
if i < 0:
    print("ERR: can't find eob1FloppyNeed")
    exit()

# Find first "\t-1\n};" after that
j = text.find("\t-1\n};", i)
if j < 0:
    print("ERR: can't find -1 terminator")
    exit()

body = text[i:j]
print(f"Body is {len(body)} chars, lines {body.count(chr(10))}")
if "kEoB1IntroStringsTower" in body:
    print("Already has intro entries (per body scan):")
    # Find where
    k = body.find("kEoB1IntroStringsTower")
    print(f"At body offset {k}: {body[max(0,k-30):k+60]!r}")
else:
    print("eob1FloppyNeed does NOT have intro entries yet — adding")
    addition = (
        "\t// Intro narration (used by Chinese fan translation)\n"
        "\tkEoB1IntroStringsTower,\n"
        "\tkEoB1IntroStringsOrb,\n"
        "\tkEoB1IntroStringsWdEntry,\n"
        "\tkEoB1IntroStringsKing,\n"
        "\tkEoB1IntroStringsHands,\n"
        "\tkEoB1IntroStringsWdExit,\n"
        "\tkEoB1IntroStringsTunnel,\n"
        "\n"
    )
    text = text[:j] + addition + text[j:]
    GAMES_CPP.write_text(text, encoding="utf-8")
    print("Added")
