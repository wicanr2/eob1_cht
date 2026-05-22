"""Apply manual translations for short strings that auto-merge missed.
Augments gen_eob1_chinese.py's lookup table."""
import re
from pathlib import Path

# Manual translations: English orig → Chinese (UTF-8)
MANUAL = {
    # Stats labels (short — 2-byte slots in original game)
    "STR": "力",
    "INT": "智",
    "WIS": "慧",
    "DEX": "敏",
    "CON": "體",
    "CHA": "魅",
    "AC\rHP\rLVL": "防\r命\r級",
    "HP": "命",

    # Yes/No labels
    "no": "否",
    "No": "否",
    "NO": "否",
    "Yes": "是",
    "YES": "是",
    "ON": "開",
    "OFF": "關",

    # Item / status messages
    "ok\r": "好\r",
    "\rok\r": "\r好\r",
    ".\r": "。\r",
    " taken.\r": " 已拿。\r",
    "%s can't wear that type of armor.\r": "%s不能穿戴此類盔甲。\r",
    "You cant put that item there.\r": "不能將物品放在那裡。\r",
    "%s can not use this item.\r": "%s無法使用此物品。\r",
    "This item automatically used when worn.\r": "此物品穿戴時自動使用。\r",
    "This item is not used in this way.\r": "此物品不能這樣使用。\r",
    "Poisoned party\rmembers will die!\rRest anyway?": "中毒隊員\r將會死亡！\r仍要休息？",
    "%s is already protected by stoneskin.\r": "%s已被石膚保護。\r",

    # Spell name
    "lay on hands": "按手治療",

    # NPC names (Forgotten Realms — usually transliterated)
    "Silvias": "希爾維亞",
    "Anya": "安雅",
    "Beohram": "畢歐拉姆",
    "Kirath": "凱拉斯",
    "Ileria": "伊蕾莉雅",
    "Tyrra": "泰拉",
    "Tod Uphill": "陶德",
    "Taghor": "塔戈",
    "Dohrum": "多倫",
    "Keirgar": "凱嘉",

    # Manual prompt (manual reference page lookup at game start)
    "\r\r\r\rOn the page with this symbol...\r\rFind line %d\rEnter word %d\r":
        "\r\r\r\r在標有此符號的頁上...\r\r找到第%d行\r輸入第%d個字\r",
}

# Write to a file that gen_eob1_chinese.py can pick up
out = Path(r"C:\Users\原來是個胖仔\scummvm_work\manual_overrides.json")
import json
out.write_text(json.dumps(MANUAL, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Wrote {len(MANUAL)} manual translations to {out}")
