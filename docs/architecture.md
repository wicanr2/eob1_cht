# EOB1 中文版 ScummVM 架構

## 整體流程

```
EOB.EXE (原 1991 SSI 遊戲檔)
  ↓ ScummVM detection: md5(EOBDATA3.PAK) + ceob.pat 存在
  ↓
GI_EOB1 + ZH_TWN flag set
  ↓
Screen_EoB::init()
  ↓ load("ceob.pat") → Big5Font::loadPrefixedRaw(f, 12)
  ↓
loadFontFile() → wraps OldDOSFont in ChineseTwoByteFontEoB
  ↓
At render time: drawChar(uint16 c, ...)
  - if c < 0x80: delegate to ASCII font
  - if c is Big5 lead (0xA1-0xFE) + trail: lookup _big5 → drawBig5Char
  ↓
String resources from KYRA.DAT (created by devtools/create_kyradat)
  - loadStrings(kEoB1MainMenuStrings) → 中文選單
  - loadStrings(kEoB1ChargenStrings1) → 中文 chargen
  - etc.
```

## ScummVM Big5 渲染棧

### Graphics::Big5Font (graphics/big5.cpp)

通用 Big5 字模 class。原本給 LOL/HOF/KYRA 中文版用。

```cpp
class Big5Font {
    void loadPrefixedRaw(Common::ReadStream &input, int height);
    bool drawBig5Char(byte *dest, uint16 ch, ...);
    bool hasGlyphForBig5Char(uint16 textChar);
    static const int kChineseTraditionalWidth = 16;
};
```

格式：
```
[uint16 BE Big5 codepoint (high bit MUST be 1)]
[(width/8) * height bytes bitmap, MSB-first within byte]
... repeat
[0xFFFF terminator]
```

### Kyra::ChineseTwoByteFontEoB (engines/kyra/graphics/screen_eob.h)

Wrapper font for EOB engine. 包住任何 single-byte font，自動處理 Big5 lead/trail：

```cpp
class ChineseTwoByteFontEoB final : public Font {
    Common::SharedPtr<Graphics::Big5Font> _big5;
    Common::ScopedPtr<Font> _singleByte;
    
    void drawChar(uint16 c, byte *dst, int pitch, int bpp) const override {
        if (c is single-byte) _singleByte->drawChar(...);
        else if (_big5->hasGlyphForBig5Char(c)) _big5->drawBig5Char(...);
    }
};
```

## ScummVM Resource System

### KYRA.DAT 格式

PAK file 結構：
1. Header: 4-byte LE offset to data + null-terminated filename × N + 4 zero bytes
2. Data block: per-resource bytes

Each resource filename = `(game << 24) | (platform << 20) | (special << 16) | (id << 4) | lang`

格式範例：`0x300A0010` = game 3 (EOB1) / platform 0 (DOS) / special 0 / id ?? / lang 10 (ZH_TWN)

### INDEX 內部結構

```
[uint32 BE version] (RESFILE_VERSION = 123)
[uint32 BE includedGames]
[uint16 BE gameDef × includedGames]
```

`gameDef = (game << 12) | (platform << 8) | (special << 4) | lang`

EOB1 ZH_TWN = `(3 << 12) | (0 << 8) | (0 << 4) | 10` = `0x300A`

### create_kyradat (devtools/)

Build-time tool. 把 C++ headers (eob1_dos_english.h, eob1_dos_chinese.h 等) 編譯成 KYRA.DAT PAK。

關鍵 tables:
- `gameDescs[]` — list of game variants (games.cpp)
- `gameNeedTable[]` — per-(game,platform,special) need list — **NOT per-lang**
- `resourceTable[]` — id → provider lookup (resources.cpp)
- ExtractFilename `langSpecific` flag — if true, file written per-lang; if false, write once with UNK_LANG

### Why need-list isn't per-lang (and why it bites us)

If `eob1FloppyNeed[]` includes `kEoB1IntroStringsTower`, then ALL game variants matching (kEoB1, DOS, kNoSpecial) — EN_ANY, DE_DEU, IT_ITA, ZH_TWN — must each have a provider that produces a file mapping to that need ID. If EN_ANY doesn't have it, `create_kyradat` errors "Could not find need <id> for game <gameDef>".

This means: adding a new ZH_TWN string that's not in any other language's source is tricky. Either:
1. Add stub English provider (hack)
2. Restructure: split into a new `kSpecial=5 ChineseFan` variant with own need list
3. Don't add — accept English fallback for those strings

We chose #3 for intro narration. Items/monsters TBD.

## 字模 build pipeline

```
E:\dos1866\eob2\CHINFONT.FNT  (encrypted 30 bytes/glyph: 2-byte LE cp + XOR-encrypted 28-byte bitmap)
                ↓
build_ceob_combined.py
  - decrypts each glyph (XOR with cp[0] for even bytes, cp[1] for odd)
  - crops 14 rows to 12 (TOP_TRIM=1)
  - for any Big5 cp not in EOB2: render from BoutiqueBitmap9x9 TTF at 12px via freetype-py
  - outputs: 2-byte BE cp + 24 byte bitmap × N + 0xFFFF terminator
                ↓
ceob.pat (357KB, 13,751 glyphs)
                ↓
copied to game dir (alongside EOB.EXE, EOBDATA*.PAK)
                ↓
ScummVM Big5Font::loadPrefixedRaw reads at startup
```

## 翻譯 pipeline

```
full_patches.json (402 entries, EOB.EXE byte offset → CHN text)
                ↓
gen_eob1_chinese.py
  - reads scummvm eob1_dos_english.h, extracts each StringProvider's English array
  - for each English string: lookup in full_patches dict (key = English text)
  - apply manual_overrides.json on top (38 short labels)
  - emit eob1_dos_chinese.h with hex-escaped CP950 bytes + /* CHN comment */
                ↓
eob1_dos_chinese.h (89 providers, 416/446 = 93%)
                ↓
register_chinese_providers.py
  - injects 90 ZH_TWN provider registrations into resources.cpp
                ↓
create_kyradat compile + run → KYRA.DAT
```

## Windows native build (MinGW-w64 cross from WSL)

```
WSL Ubuntu-22.04
  ↓
apt install mingw-w64 libz-mingw-w64-dev
  ↓
download SDL2-devel-2.30.7-mingw.tar.gz → /opt/sdl2-mingw/
  ↓
./configure --host=x86_64-w64-mingw32 --with-sdl-prefix=/opt/...
            --backend=sdl --disable-all-engines --enable-engine=kyra,eob
            --disable-translation --disable-flac --disable-vorbis
            ... (minimal feature set)
  ↓
make -j8
  ↓
scummvm.exe (99MB unstripped, 27MB stripped)
  ↓
x86_64-w64-mingw32-strip scummvm.exe → 27MB
  ↓
ship with SDL2.dll
```

## Detection 為何要 ceob.pat 存在?

不想跟 EN_ANY entry 衝突（同 MD5），所以多加一個 AD_ENTRY 檢查 ceob.pat 是否存在。沒裝 ceob.pat 的人 → 看不到 ZH_TWN entry，detection 正常 fall back EN_ANY。

```cpp
// engines/kyra/detection_tables.h
{
    "eob",
    "Extracted",
    AD_ENTRY2s("EOBDATA3.PAK", "61aff543131bd61a8b7d7dc901a8278b", AD_NO_SIZE,
               "ceob.pat",     NULL,                               AD_NO_SIZE),
    Common::ZH_TWN,
    ...
},
```
