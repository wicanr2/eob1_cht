"""Generate eob1_dos_chinese.h from eob1_dos_english.h + translation sources.

Sources of translation (priority order):
  1. full_patches.json — EOB.EXE byte-offset translations (most reliable, hand-tuned)
  2. eob2_dos_chinese.h — for D&D terms (race/class/spell/alignment) identical between EOB1/2
  3. Fallback: leave English as-is (game will show ASCII for that string)

Output format mirrors eob2_dos_chinese.h:
  - Hex-escaped Big5 bytes
  - Trailing `/* "中文" */` comment for human readability

Usage:
  python gen_eob1_chinese.py
"""
import json, re, sys
from pathlib import Path

ROOT = Path(r"C:\Users\原來是個胖仔\scummvm_work\scummvm")
ENG_H = ROOT / "devtools/create_kyradat/resources/eob1_dos_english.h"
EOB2_CHN_H = ROOT / "devtools/create_kyradat/resources/eob2_dos_chinese.h"
OUT_H = ROOT / "devtools/create_kyradat/resources/eob1_dos_chinese.h"
FULL_PATCHES = Path(r"C:\Users\原來是個胖仔\eob_analysis\full_patches.json")

# -------- Parse C string arrays --------
ARR_RE = re.compile(
    r"static const char \*const (kEoB1\w+DOSEnglish)\[(\d+)\]\s*=\s*\{(.*?)\};",
    re.DOTALL
)

def parse_c_strings(text, suffix):
    """Return [(name_without_suffix, count, [string1, string2,...]), ...]"""
    arrays = []
    for m in re.finditer(
        rf"static const char \*const (kEoB1\w+){suffix}\[(\d+)\]\s*=\s*\{{(.*?)\}};",
        text, re.DOTALL
    ):
        name = m.group(1)
        count = int(m.group(2))
        body = m.group(3)
        strings = parse_string_literals(body)
        arrays.append((name, count, strings))
    return arrays

def parse_string_literals(body):
    """Parse C string literals (handles concatenation, hex escapes). Returns list of str values (bytes-as-str)."""
    items = []
    # Split by top-level commas (not inside strings)
    cur_strs = []
    in_str = False
    esc = False
    buf = ""
    i = 0
    while i < len(body):
        c = body[i]
        if not in_str:
            if c == '"':
                in_str = True
                buf = ""
            elif c == ',':
                if cur_strs:
                    items.append("".join(cur_strs))
                    cur_strs = []
            elif c.isspace():
                pass
            elif c == '/':  # comment
                if body[i:i+2] == '//':
                    nl = body.find('\n', i)
                    i = nl if nl >= 0 else len(body)
                elif body[i:i+2] == '/*':
                    end = body.find('*/', i)
                    i = end + 2 if end >= 0 else len(body)
                    continue
        else:
            if esc:
                # Handle \xNN, \r, \n, etc
                if c == 'x':
                    hex_str = body[i+1:i+3]
                    buf += chr(int(hex_str, 16))
                    i += 2
                elif c == 'r': buf += '\r'
                elif c == 'n': buf += '\n'
                elif c == 't': buf += '\t'
                elif c == '0': buf += '\0'
                elif c == '\\': buf += '\\'
                elif c == '"': buf += '"'
                else: buf += c
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                in_str = False
                cur_strs.append(buf)
            else:
                buf += c
        i += 1
    if cur_strs:
        items.append("".join(cur_strs))
    return items

# -------- Build translation lookup --------
def build_lookup():
    """English (cleaned) → Chinese bytes (cp950)."""
    lookup = {}
    # Source 1: full_patches.json
    with open(FULL_PATCHES, encoding="utf-8") as f:
        patches = json.load(f)
    for k, v in patches.items():
        if k.startswith("_"): continue
        orig = v.get("orig", "")
        new = v.get("new", "")
        if not orig or not new: continue
        # Handle CR-separated compound (split into individual lines)
        if "\r" in orig and "\r" in new:
            o_parts = orig.split("\r")
            n_parts = new.split("\r")
            if len(o_parts) == len(n_parts):
                for op, np in zip(o_parts, n_parts):
                    op = op.strip()
                    np = np.strip()
                    if op and np:
                        lookup[op] = np
        # Always also add the full compound
        lookup[orig] = new
        # Add a no-space version too
        lookup[orig.strip()] = new

    # Source 2: eob2_dos_chinese.h (for D&D terms)
    if EOB2_CHN_H.exists():
        text = EOB2_CHN_H.read_text(encoding="utf-8", errors="replace")
        # Parse "string" /* "中文" */ comment pairs — comments are CHN reference
        # Actually format is: "hex-escaped-bytes" /* "中文" */
        # We need to map English (from eob1) → CHN. But eob2 file doesn't have English.
        # Skip this for now; user can hand-merge later.

    # Source 3: manual_overrides.json — hand-tuned translations for short labels
    manual_path = Path(r"C:\Users\原來是個胖仔\scummvm_work\manual_overrides.json")
    if manual_path.exists():
        with open(manual_path, encoding="utf-8") as f:
            manual = json.load(f)
        for k, v in manual.items():
            lookup[k] = v
        print(f"Loaded {len(manual)} manual overrides")

    return lookup

# -------- Encode string for C source --------
def encode_cpp(s):
    """Take a str and emit it as escaped C bytes (cp950 encoded), with CHN comment."""
    try:
        b = s.encode("cp950")
    except UnicodeEncodeError:
        b = s.encode("cp950", errors="replace")
    parts = []
    chn_chars = []
    i = 0
    while i < len(b):
        byte = b[i]
        if byte == 0x0D: parts.append("\\r")
        elif byte == 0x0A: parts.append("\\n")
        elif byte == 0x09: parts.append("\\t")
        elif byte == 0x00: parts.append("\\0")
        elif byte == 0x22: parts.append("\\\"")
        elif byte == 0x5C: parts.append("\\\\")
        elif 0xA1 <= byte <= 0xFE and i + 1 < len(b):
            # Big5 lead
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
    return "".join(parts), "".join(chn_chars)

def main():
    print(f"Reading {ENG_H}")
    eng_text = ENG_H.read_text(encoding="utf-8", errors="replace")
    arrays = parse_c_strings(eng_text, "DOSEnglish")
    print(f"Parsed {len(arrays)} string arrays from English source")

    lookup = build_lookup()
    print(f"Loaded {len(lookup)} translation pairs from sources")

    # Generate output
    out_lines = []
    out_lines.append("// Auto-generated by gen_eob1_chinese.py")
    out_lines.append("// Translations sourced from EOB1 EXE patch + manual edits")
    out_lines.append("// Strings without translations are intentionally left in English as fallback")
    out_lines.append("")
    total_strs = 0
    translated = 0
    for name, count, strings in arrays:
        chn_name = name + "DOSChinese"
        out_lines.append(f"static const char *const {chn_name}[{count}] = {{")
        for s in strings:
            total_strs += 1
            if s in lookup:
                chn = lookup[s]
                translated += 1
            else:
                # Try stripped
                key = s.strip()
                if key in lookup:
                    chn = lookup[key]
                    # Preserve leading/trailing whitespace from original
                    lead = s[:len(s) - len(s.lstrip())]
                    trail = s[len(s.rstrip()):]
                    chn = lead + chn + trail
                    translated += 1
                else:
                    chn = s  # English fallback
            esc, comment = encode_cpp(chn)
            cmt = f" /* \"{comment}\" */" if comment else ""
            out_lines.append(f"\t\"{esc}\",{cmt}")
        out_lines.append("};")
        out_lines.append("")
        out_lines.append(f"static const StringListProvider {chn_name}Provider = {{ ARRAYSIZE({chn_name}), {chn_name} }};")
        out_lines.append("")
    OUT_H.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"Wrote {OUT_H}")
    print(f"Translation coverage: {translated}/{total_strs} ({100*translated/max(1,total_strs):.1f}%)")

if __name__ == "__main__":
    main()
