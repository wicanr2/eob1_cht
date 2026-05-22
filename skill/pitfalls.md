# 完整踩坑清單

歷史上踩過的每個坑 + fix。下次省時間用。

## 字串 patch 階段

### 坑 1: cp950 vs cp936 編碼差
台灣繁體 Big5 = cp950，跟簡體 cp936 (GBK) 不同。一定要用 `text.encode("cp950")`。錯用 cp936 會產生壞 codepoint，subset 找不到字模。

### 坑 2: slot 長度算錯
slot 從字串起點到下個 null byte。如果新字串 > slot，會吃到下一條字串的開頭，整個翻譯壞掉。
**Fix**: `patch_exe_strings.py` 會自動驗證並 reject 太長的字串。

### 坑 3: 翻譯包含半形冒號 vs 全形冒號
"Select Option:" → "選擇:" (半形)會吃掉後面 byte，建議用"選擇：" (全形冒號)避免。
**注意**: 部分標點 Big5 codepoint 不在 53 字 demo subset 內 (0xA143 0xA147 0xBED0 等)，要 patch 前先擴 subset。

## OVL hook 階段

### 坑 4: Big5 endianness (最常踩)
詳見 `hook_internals.md`。簡而言之: `mov al, lead; mov ah, trail; mov bx, ax` 是對的；任何 xchg 都是錯的。

### 坑 5: Search loop `je` 跨度算錯
原版錯誤代碼:
```
je +5        ; 2 bytes  → 跳到 0x2C9B
add si, 30   ; 3 bytes
loop search  ; 2 bytes  → 0x2C9B
.not_found:
jmp normal   ; 3 bytes
.found:
add si, 2    ; ← je +5 應該跳到這裡，但實際跳到 .not_found
```
`je +5` 從下一指令 IP 算 +5 byte，正好跳到「not found jmp normal」起點，不是 found。應該是 `je +8` 跳過 `add si,30 + loop + jmp` 三個指令 = 3+2+3 = 8 bytes。

### 坑 6: `loop -9` 跳進 cmp 指令中間
原版錯誤: `loop -9` 從 next IP 跳 -9，落在 `cmp [si], bx` (3 bytes 指令) 的中間 byte 0x39 處 → 變成 `cmp ax, [si]` 不帶 CS prefix → 讀 DS 而不是 CS → 比對錯誤資料 → 永遠 not match。
**Fix**: `loop -10` 跳回 cmp 起點 (CS-prefix `2E` byte)。

### 坑 7: `ja +3` 落在指令中間
原版錯誤代碼:
```
cmp ah, 0x7E
ja +3       ; 跳過下面 2-byte EB rel8
EB 10       ; jmp short to valid_trail (2 bytes)
cmp ah, 0xA1
```
`ja +3` 從下一指令 IP 跳 +3，但 `EB 10` 只 2 bytes，+3 落在下下個指令 (`cmp ah, 0xA1` = `80 FC A1`) 中間。實際執行 `FC A1 73 03` = cld + mov ax,[373h] + ... 亂跑。
**Fix**: `ja +2` 跳過 2-byte 短 jmp。

### 坑 8: 不做 const patch
不做的話 EOB scratch buffer 從 image 0x2C40 開始寫 16KB 以上，把 hook 蓋成垃圾 → 遊戲 crash 或停在標題畫面。Const patch 改 `mov bx, 0x2C38` → `mov bx, 0x4000` 把 scratch 推到 image 0x4000+。

### 坑 9: 找錯 hook 點 (0x27FD vs 0x241E)
0x27FD 是 OVL 內部的 `call orig_blit` 一個 call site。Hook 這裡只能攔截 OVL per-char dispatch loop 的字。CAMP menu 跟角色生成有些畫面用 EOB.EXE 直接 far-call orig_blit，會繞過 0x27FD hook。
**Fix**: hook 裝在 orig_blit (image 0x241E) 入口本身，所有路徑都進來。

### 坑 10: Hook 放在 "閒置" 區域被覆寫
試過幾個地方都壞:
- image 0x020B (287 byte 零區) — runtime 被當 buffer 寫
- image 0x3000 (檔尾擴充區) — EOB scratch 蓋到
- image 0x2C38 + 21 bytes 剛好不壞 (歷史巧合)
**Fix**: const patch 後放在 image 0x2D80 安全。

### 坑 11: MZ header e_cp 改了 e_cblp 沒同步
```python
new_ecp = (len(data) + 511) // 512
data[4:6] = new_ecp.to_bytes(2, 'little')
e_cblp = len(data) - (new_ecp - 1) * 512
if e_cblp == 512: e_cblp = 0
data[2:4] = e_cblp.to_bytes(2, 'little')
```
不做 e_cblp 同步，DOS 算出來的檔大小錯，要嘛少載要嘛多載，OVL 壞掉。

### 坑 12: 8 push / 7 pop 不對稱
Hook 入口 push 8 個 (含 bp)，pop 也要 8 個。或者 push 7 個再 push bp 然後 mov bp, sp，pop 順序反過來。最容易漏 pop bp。

### 坑 13: ASCII fall-through 沒重建 bp 框架
從我們 hook 跳回 `orig_blit + 3` 時，stack 要長得像 orig_blit 已執行完 `push bp; mov bp, sp` 的樣子。所以我們要 pop 自己的所有 saved regs (含 bp)，再 `push bp; mov bp, sp` 一次，才 jmp orig_blit+3。

### 坑 14: 寫到 VGA buffer 外
`mov al, [bp+18]` 讀字 word，但只低 byte 才是 char。如果直接 `mov di, [bp+18]` 再算偏移，高 byte 可能不是 0 → di 變很大 → 寫到 VGA buffer 外亂搞。
**Fix**: 先 `mov bl, [bp+18]; xor bh, bh; mov di, bx` 確保只用低 byte。

## 遊戲 / DOSBox 階段

### 坑 15: 啟動提示沒過
EOB1 啟動會問 4=VGA / 1=AdLib / y=Mouse。沒回應就停那。
**Fix**: 用 `PAUSE6K.COM` + `enter41Y.COM` 在 game.conf `[autoexec]` 自動答。檔在 GAME/ 目錄。

### 坑 16: DOSBox 視窗截圖
`PrintWindow(hwnd, hdc, 2)` flag=2 可截 DOSBox 不在 foreground 也行。flag=0 會截到桌面背景。

### 坑 17: 自動化送鍵盤失敗
SendKeys / PostMessage 都被 DOSBox 吃掉。必須先 mouse left click DOSBox window center 取得 focus。

### 坑 18: EOB palette 不是標準 VGA
- Color 4 顯示為**綠色** (不是紅)
- Color 5 顯示不明顯
- 醒目: 14 (黃), 15 (白), 12 (橘/淺紅)
診斷標記用 14 或 15 最安全。

### 坑 19: Plan 1-2 OVL 不要 restore 成沒 patch 過的 pristine
否則 byte-pair Chinese 都沒了，整個畫面變成「Big5 高 bit 被 strip 成 ASCII 控制字符」，遊戲變空白。永遠從 `MCGA_CHT.OVL` (= pristine + 0x27FA 0xFF patch) 開始建。

## Cosmetic 待修

### 坑 20: 字模太高蓋下一行
14 px 高字模在 10 px 行距的 menu (e.g., SELECT CLASS) 會疊。
**TODO**: 偵測 row spacing 動態調整 height，或硬改成 8 rows。

### 坑 21: 字模前偶有 "J" 殘留
疑似某條 lead byte 路徑沒被 hook 攔到，被當 ASCII rendered 出來。
**TODO**: trace 是哪條 caller path。
