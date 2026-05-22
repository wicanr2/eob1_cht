"""Append Chinese intro narration string providers to eob1_dos_chinese.h.
These mirror the Spanish version's coverage (kEoB1IntroStringsTower/Orb/King/Hands/WdEntry/WdExit/Tunnel).
"""
from pathlib import Path

CHN_H = Path(r"C:\Users\原來是個胖仔\scummvm_work\scummvm\devtools\create_kyradat\resources\eob1_dos_chinese.h")

# Chinese translations of the intro narration
INTRO_STRINGS = {
    "Tower": [
        "我等，深水城的領主們，\r齊聚於此，誓欲清除\r古老邪惡，淨化吾城。",
        "",
        "我等召集本區英雄，\r選出吾等之勇士。",
    ],
    "Orb": [
        "偉大的祭司...",
    ],
    "WdEntry": [
        "看來我等找到了\r可行之解決方法。",
    ],
    "King": [
        "我等委託諸位\r消滅這些惡魔...\r若諸位辦得到。",
    ],
    "Hands": [
        "為這趟危險旅程\r做好準備吧。",
    ],
    "WdExit": [
        "前往城下開始你們的搜索。",
    ],
    "Tunnel": [
        "冒險開始了。",
        "出口被擋住了！",
    ],
}

def encode_cpp(s):
    """Convert UTF-8 str -> Big5 escape sequence + decode comment."""
    if not s:
        return '""', ""
    b = s.encode("cp950", errors="replace")
    parts = []
    chn_chars = []
    i = 0
    while i < len(b):
        byte = b[i]
        if byte == 0x0D: parts.append("\\r")
        elif byte == 0x0A: parts.append("\\n")
        elif byte == 0x22: parts.append("\\\"")
        elif byte == 0x5C: parts.append("\\\\")
        elif 0xA1 <= byte <= 0xFE and i + 1 < len(b):
            trail = b[i+1]
            parts.append(f"\\x{byte:02x}\\x{trail:02x}")
            try:
                chn_chars.append(bytes([byte, trail]).decode("cp950"))
            except: chn_chars.append("?")
            i += 1
        elif 0x20 <= byte < 0x7F:
            parts.append(chr(byte))
        else:
            parts.append(f"\\x{byte:02x}")
        i += 1
    return '"' + "".join(parts) + '"', "".join(chn_chars)

# Build C++ source
new_block = ["\n// Intro narration (mirrors Spanish version) — added for Chinese fan translation"]
for key, strings in INTRO_STRINGS.items():
    arr_name = f"kEoB1IntroStrings{key}DOSChinese"
    new_block.append(f"\nstatic const char *const {arr_name}[{len(strings)}] = {{")
    for s in strings:
        escaped, comment = encode_cpp(s)
        cmt = f" /* \"{comment}\" */" if comment else ""
        new_block.append(f"\t{escaped},{cmt}")
    new_block.append("};")
    new_block.append("")
    new_block.append(f"static const StringListProvider {arr_name}Provider = {{ ARRAYSIZE({arr_name}), {arr_name} }};")

text = CHN_H.read_text(encoding="utf-8")
text += "\n".join(new_block) + "\n"
CHN_H.write_text(text, encoding="utf-8")
print(f"Added {len(INTRO_STRINGS)} intro string providers to {CHN_H}")
