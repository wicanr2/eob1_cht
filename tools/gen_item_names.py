"""Generate C arrays for kEoB1ItemNamesDOSEnglish / kEoB1ItemNamesDOSChinese.

Output: paste-ready C blocks for eob1_dos_chinese.h + a new eob1_dos_english.h.

Big5 chars are 2 bytes each. Item name buffer = 35 bytes max (per items_eob.cpp).
"""
from pathlib import Path

# 95 EN names extracted via extract_item_names2.py
EN = [
    'Mouse Pointer', '', 'Leather armor', 'Robe', 'Staff', 'Dagger', 'Short sword',
    'Lock picks', 'Spellbook', 'Cleric Holy symbol', 'Leather boots', 'Iron Rations',
    'NULL', 'Jeweled Key', 'Potion', 'Gem', 'Skull Key', 'Wand', 'Scroll', 'Ring',
    'Ring of Protection +2', 'Adamantite Dart', 'Paladin Holy Symbol',
    'Wand of Slivias', 'Dwarf Bones', 'Key', 'Commission and Letter of Marque',
    'Axe', 'Dart', 'Halberd', 'Chainmail', 'Helmet', 'Dwarf Helmet', 'Silver Key',
    'Adamantite Long Sword', 'Mace', 'Longsword', "'Guinsoo'", 'Orb of Power',
    'Dwarven Healing Potion', 'Rock', 'Rations', 'Fancy Robe', 'Igneous Rock',
    'Spear', 'Stone Medallion', 'Halfling Bones', 'Arrow', 'Shield', 'Gold Key',
    'Bow', 'Stone dagger', 'Sling', "'Backstabber'", 'Long Sword', 'Dwarven Key',
    'Medallion', 'Medallion of Adornment', "'Drow Cleaver'", 'Stone Scepter',
    'Dwarven Helmet', 'Dwarven Shield', 'Stone Necklace', 'Plate Mail', 'Scale Mail',
    'Boots', 'Kenku Egg', 'Stone Ring', 'Bracers', 'Chieftain Halberd', 'Necklace',
    'Necklace of Adornment', 'Luck Stone Medallion', "'Slicer'", 'Banded Armor',
    'Drow Key', 'Ruby Key', "'Night Stalker'", 'Drow Bow', 'Drow Boots',
    'Plate Mail of Great Beauty', 'Flail', 'Scepter of Kingly Might', 'Drow Shield',
    'Stone Holy Symbol', 'Stone Orb', "'Slasher'", 'Robe of Defense', "'Flicka'",
    'Human Bones', "'Severious'", 'Wand of Fireballs', 'Cure Poison Potion',
    'Holy Symbol', 'Spell Book',
]

# Traditional Chinese translations (standard AD&D 2e Chinese localization).
# Each must encode to < 35 bytes in cp950 (Big5).
ZH = [
    '滑鼠指標', '', '皮甲', '長袍', '法杖', '匕首', '短劍',
    '開鎖工具', '法術書', '牧師聖符', '皮靴', '鐵糧',
    'NULL', '寶石鑰匙', '藥水', '寶石', '骷髏鑰匙', '魔杖', '卷軸', '戒指',
    '+2 防護戒指', '精金擲鏢', '聖騎聖符',
    '史利維亞魔杖', '矮人遺骨', '鑰匙', '委任狀',
    '斧', '擲鏢', '戟', '鎖甲', '頭盔', '矮人盔', '銀鑰匙',
    '精金長劍', '釘頭錘', '長劍', '鬼引劍', '力量魔球',
    '矮人治療藥水', '石塊', '糧食', '華麗長袍', '火成岩',
    '矛', '石製徽章', '半身人遺骨', '箭', '盾牌', '金鑰匙',
    '弓', '石製匕首', '投石索', '背刺者', '長劍', '矮人鑰匙',
    '徽章', '裝飾徽章', '卓爾劈砍劍', '石製權杖',
    '矮人頭盔', '矮人盾', '石製項鍊', '板甲', '鱗甲',
    '靴子', '鳥人蛋', '石製戒指', '護腕', '酋長戟', '項鍊',
    '裝飾項鍊', '幸運石徽章', '切片劍', '環甲',
    '卓爾鑰匙', '紅寶石鑰匙', '夜行者', '卓爾弓', '卓爾靴',
    '美貌板甲', '連枷', '王者權杖', '卓爾盾',
    '石製聖符', '石製魔球', '揮砍者', '防禦長袍', '弗利卡',
    '人類遺骨', '賽維拉斯', '火球魔杖', '解毒藥水',
    '聖符', '法術書',
]

assert len(EN) == 95 == len(ZH), f"len mismatch EN={len(EN)} ZH={len(ZH)}"


def to_c_escape_ascii(s):
    """Escape ASCII string for C literal."""
    out = ''
    for ch in s:
        if ch == '\\':
            out += '\\\\'
        elif ch == '"':
            out += '\\"'
        elif 0x20 <= ord(ch) <= 0x7E:
            out += ch
        else:
            out += f'\\x{ord(ch):02x}'
    return out


def to_c_escape_big5(s):
    """Encode Chinese string to cp950 (Big5) and emit as C \\xNN escapes.
    ASCII chars stay as literals."""
    if not s:
        return ''
    out = ''
    raw = s.encode('cp950')
    i = 0
    while i < len(raw):
        b = raw[i]
        if 0x20 <= b <= 0x7E and b != ord('\\') and b != ord('"'):
            # ASCII printable
            out += chr(b)
            i += 1
        elif b >= 0x80 and i + 1 < len(raw):
            # Big5 lead byte → emit both bytes as \x escapes
            out += f'\\x{b:02x}\\x{raw[i+1]:02x}'
            i += 2
        else:
            out += f'\\x{b:02x}'
            i += 1
    return out


def emit_array(name, items, encoder, comment=None):
    lines = []
    if comment:
        lines.append(f'// {comment}')
    lines.append(f'static const char *const {name}[{len(items)}] = {{')
    for i, s in enumerate(items):
        esc = encoder(s)
        comment = f' /* "{s}" */' if encoder is to_c_escape_big5 and s else ''
        lines.append(f'\t"{esc}",{comment}')
    lines.append('};')
    lines.append('')
    lines.append(f'static const StringListProvider {name}Provider = '
                 f'{{ ARRAYSIZE({name}), {name} }};')
    return '\n'.join(lines)


# Sanity check: every Chinese string fits in 34 bytes (35 incl null)
for i, (e, z) in enumerate(zip(EN, ZH)):
    z_bytes = z.encode('cp950') if z else b''
    if len(z_bytes) > 34:
        print(f"WARN [{i}] '{z}' = {len(z_bytes)} bytes (over 34)")


root = Path(r'D:\03_game_tmp\eob1_cht\tools')
en_out = root / 'item_names_en_block.c'
zh_out = root / 'item_names_zh_block.c'

en_out.write_text(
    emit_array('kEoB1ItemNamesDOSEnglish', EN, to_c_escape_ascii,
               comment='95 EN item names (extracted from EOBDATA6.PAK/ITEM.DAT)'),
    encoding='utf-8')

zh_out.write_text(
    emit_array('kEoB1ItemNamesDOSChinese', ZH, to_c_escape_big5,
               comment='95 ZH item names (standard AD&D 2e 中文)'),
    encoding='utf-8')

print(f"Wrote {en_out}")
print(f"Wrote {zh_out}")
print(f"\nLength check:")
print(f"  EN max bytes = {max(len(e) for e in EN)}")
print(f"  ZH max bytes = {max(len(z.encode('cp950')) for z in ZH if z)}")
