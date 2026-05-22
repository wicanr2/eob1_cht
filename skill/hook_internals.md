# orig_blit Prefix Hook 組合語言細節

## 為什麼選 orig_blit prefix

EOB.EXE 渲染文字有多條路徑:
1. **MCGA.OVL 內部 per-char dispatch** (image 0x27F4-0x280B), 在 0x27FD 處 `call orig_blit`
2. **EOB.EXE 自己直接 far-call orig_blit** (CAMP menu / 角色生成等)

如果只 hook 0x27FD call site，路徑 2 漏掉。所以裝在 **orig_blit (image 0x241E) 入口** 才能攔截全部。

## 原始 orig_blit 結構

```
0x241E  55          push bp
0x241F  8B EC       mov bp, sp
0x2421  53          push bx
0x2422  57          push di
0x2423  06          push es
0x2424  56          push si
0x2425  2E 8E 06 05 00  mov es, cs:[0x0005]   ; font segment (globals at OVL start)
0x242A  2E 8B 36 03 00  mov si, cs:[0x0003]   ; font offset
0x242F  26 8B 44 02     mov ax, es:[si+2]
0x2433  26 8B 34        mov si, es:[si]
0x2436  8E C0       mov es, ax
0x2438  8B 5E 04    mov bx, [bp+4]    ; bx = char arg
0x243B  43          inc bx
0x243C  D1 E3       shl bx, 1
0x243E  26 8B 18    mov bx, es:[bx+si]  ; lookup glyph offset in font table
0x2441  8B 56 06    mov dx, [bp+6]    ; dx = x arg
0x2444  81 FA 40 01 cmp dx, 0x140 (=320)
... bounds check ...
0x2468  8B 56 08    mov dx, [bp+8]    ; dx = y arg
0x246B  81 FA C8 00 cmp dx, 0xC8 (=200)
... 然後 8-bit-wide blit 到 (x, y) ...
```

Args: `[bp+4]=char`, `[bp+6]=x`, `[bp+8]=y`。Caller push 順序 `push y; push x; push char; call orig_blit`。

## Hook 安裝

把首 3 bytes `55 8B EC` 改成 `E9 rel16`:
```
0x241E  E9 lo hi    jmp HOOK_IMG  ; lo,hi = HOOK_IMG - (0x241E + 3)
```
For HOOK_IMG = 0x2D80: rel = 0x095F → bytes `E9 5F 09`。

## Hook 程式 (image 0x2D80)

### Entry (儲存 regs + setup bp)

```asm
50          push ax
53          push bx
51          push cx
52          push dx
56          push si
57          push di
06          push es
55          push bp
8B EC       mov bp, sp
```

Stack layout after this:
```
[bp+0]  old bp (pushed)
[bp+2]  es
[bp+4]  di
[bp+6]  si
[bp+8]  dx
[bp+10] cx
[bp+12] bx
[bp+14] ax
[bp+16] ret IP (from CALL to orig_blit)
[bp+18] char arg
[bp+20] x arg
[bp+22] y arg
```

### Read char + check lead_pending

```asm
8A 46 12         mov al, [bp+18]            ; al = char
2E 8A 26 lo hi   mov ah, cs:[lead_pending]
0A E4            or ah, ah
75 03            jne +3                      ; if pending, fall through (trail)
E9 lo hi         jmp not_pending             ; else (rel16, may be far)
```

### TRAIL byte path (pending=1)

```asm
2E C6 06 lo hi 00   mov byte cs:[lead_pending], 0
; al still has trail
; build bx = ah:al where ah=trail, al=lead (LE-encoded codepoint)
88 C4               mov ah, al                 ; ah = trail
2E A0 lo hi         mov al, cs:[saved_lead]    ; al = lead
8B D8               mov bx, ax                 ; bx = trail:lead

; Linear search subset
BE lo hi            mov si, subset_data
B9 35 00            mov cx, 53                 ; entry count
search:
  2E 39 1C          cmp word cs:[si], bx       ; LE-read = trail:lead matches
  74 08             je found                    ; +8: skip add+loop+jmp
  83 C6 1E          add si, 30                  ; next entry
  E2 F6             loop search                 ; -10: back to cmp
E9 lo hi            jmp ret_no_render           ; not found

found:
  83 C6 02          add si, 2                   ; past codepoint to bitmap
  ; compute di = y*320 + (x - 8)
  8B 46 16          mov ax, [bp+22]             ; y
  8B D0             mov dx, ax
  C1 E0 06          shl ax, 6                   ; y*64
  C1 E2 08          shl dx, 8                   ; y*256
  01 D0             add ax, dx                  ; y*320
  03 46 14          add ax, [bp+20]             ; +x
  83 E8 08          sub ax, 8                   ; -8 (lead's position before cursor advanced)
  8B F8             mov di, ax
  B8 00 A0          mov ax, 0xA000
  8E C0             mov es, ax
  2E A0 35 20       mov al, cs:[0x2035]         ; FG color

  ; 14 row × 16 col blit
  B9 0E 00          mov cx, 14
row:
  51                push cx
  2E 8A 24          mov ah, cs:[si]             ; left 8 bits
  2E 8A 54 01       mov dl, cs:[si+1]           ; right 8 bits
  83 C6 02          add si, 2
  B9 08 00          mov cx, 8
left:
  D0 E4             shl ah, 1                   ; MSB → CF
  73 03             jae +3                      ; if CF=0 skip
  26 88 05          mov es:[di], al
  47                inc di
  E2 F6             loop left
  B9 08 00          mov cx, 8
right:
  D0 E2             shl dl, 1
  73 03             jae +3
  26 88 05          mov es:[di], al
  47                inc di
  E2 F6             loop right
  81 C7 30 01       add di, 304                 ; next row = 320-16
  59                pop cx
  E2 D4             loop row

E9 lo hi            jmp ret_no_render
```

### NOT_PENDING (check if lead byte)

```asm
not_pending:
  3C A1             cmp al, 0xA1
  73 03             jae +3
  E9 lo hi          jmp ascii                   ; al < 0xA1
  3C FE             cmp al, 0xFE
  76 03             jbe +3
  E9 lo hi          jmp ascii                   ; al > 0xFE

  ; valid lead
  2E A2 lo hi       mov cs:[saved_lead], al
  2E C6 06 lo hi 01 mov byte cs:[lead_pending], 1
  E9 lo hi          jmp ret_no_render
```

### RET (no render)

```asm
ret_no_render:
  5D                pop bp
  07                pop es
  5F                pop di
  5E                pop si
  5A                pop dx
  59                pop cx
  5B                pop bx
  58                pop ax
  C3                ret
```

### ASCII fall-through to orig_blit

```asm
ascii:
  5D                pop bp
  07 5F 5E 5A 59 5B 58   pop es,di,si,dx,cx,bx,ax
  ; stack now: [ret IP, char, x, y]
  55                push bp                     ; replicate orig_blit prologue
  8B EC             mov bp, sp
  E9 lo hi          jmp orig_blit_plus3         ; = 0x2421 (after our patched 3 bytes)
```

### Data area

```asm
lead_pending: db 0
saved_lead:   db 0
subset_data:  ds (hook_subset.bin content from offset 8 onwards = strip CHST header)
```

## Endianness 對齊 (最關鍵)

Subset file (`hook_subset.bin`) header `CHST` + count + glyph_size + records.
Each record: 2 bytes BE codepoint + 28 bytes bitmap.

For char "戰" (0xBE54):
- File bytes: `BE 54 ...bitmap...` (lead first, trail second = BIG-ENDIAN)
- x86 `cmp word [si], bx` reads as LE word = `0x54BE` (low byte first)

So `bx` must equal `0x54BE` to match.

When hook receives lead byte 0xBE then trail byte 0x54:
- After `mov al, [bp+18]` (trail call): `al = 0x54`
- We want `ah = 0x54` (trail) and `al = 0xBE` (lead, from saved_lead)
- After `mov ah, al` then `mov al, cs:[saved_lead]`: `ax = 0x54BE` ✓
- `mov bx, ax` → bx = 0x54BE = matches LE-read of `BE 54`

If you accidentally use `xchg al, ah` after, you get `ax = 0xBE54` (BE integer), which is the WRONG value. Search will fail.

## Const patch (避免 hook 被覆寫)

MCGA.OVL image 0x0C3F 有個函式回傳 `bx = ROUND_UP(image_size_bytes / 16)` 作為 paragraph 數。EOB.EXE caller 用這個算「我可以在 (CS+bx):0 後面當 scratch buffer」。

原值 `BB 38 2C` = `mov bx, 0x2C38`，shr 4 + inc → bx = 0x2C4。所以 EOB scratch 從 image 0x2C40 (= 0x2C4 * 16) 開始寫。

如果 hook 放在 image 0x2D80，EOB scratch 寫到 0x2C40..0xC2C40 全蓋掉 hook 區。Hook bytes 變垃圾，遊戲 crash 或 hang。

**Fix**: patch file 0x0E4D..0x0E4E `38 2C` → `00 40`。函式回傳 bx = 0x401，EOB scratch 從 image 0x4010 開始寫。Hook 在 image 0x2D80..0x34xx 安全。
