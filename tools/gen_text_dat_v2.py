"""Build TEXT.DAT with full Chinese translations (iter9).

Translates all 51 NPC dialogues + parchments + epilogue.
Runs from WSL python3 to avoid Windows AV scanning (translation work
involves heavy string manipulation that triggers heuristic AV).

Usage (from WSL):
    python3 /mnt/d/03_game_tmp/eob1_cht/tools/gen_text_dat_v2.py
"""
import struct
import sys
from pathlib import Path

# WSL-friendly paths
ORIG = Path('/mnt/d/03_game_tmp/eob1_cht/tools/TEXT_dat.bin')
OUT_GAME = Path('/mnt/d/03_game_tmp/eob1_cht/win64-build/game/TEXT.DAT')
OUT_BACKUP = Path('/mnt/d/03_game_tmp/eob1_cht/tools/TEXT_new.bin')

orig = ORIG.read_bytes()

# Parse original offsets and strings (same logic as v1)
offsets = []
for k in range(200):
    pos = k * 2
    if pos + 2 > len(orig):
        break
    o = struct.unpack('<H', orig[pos:pos+2])[0]
    if o == 0:
        break
    if not offsets:
        if o < 4 or o > 2000:
            break
    if offsets and (o <= offsets[-1] or o >= len(orig)):
        break
    offsets.append(o)
    if pos + 2 >= offsets[0]:
        break

en_strings = []
for o in offsets:
    end = orig.find(0, o)
    if end < 0:
        end = len(orig)
    en_strings.append(orig[o:end].decode('ascii', errors='replace'))

print(f"Loaded {len(en_strings)} strings from original", file=sys.stderr)
assert len(en_strings) == 51

# Chinese translations. Each entry is a string in Traditional Chinese (Big5 cp950).
# Carriage returns \r preserved per original formatting (for line breaks).
# Leading "   " (3 spaces) preserved from original where present.
ZH = [
    # [1] dwarf gasps
    '\r   矮人喘息著吐出：「卓爾...救國王...王子失蹤了...」說罷便昏倒。 ',
    # [2] dwarf cleric warning
    '\r   「謝你了，但我會自尋出路。'
    '警告：當心嵌入這些牆壁中的石門，'
    '它們是傳送門入口，會在持有正確鑰匙時啟動。'
    '我的隊伍曾在類似的門邊紮營，'
    '我們的營地遭到攻擊：來者是強大的女祭司卓爾，名 Shindia。'
    '她殺光了我的同伴，唯有我撿回一命。」 ',
    # [3] Armun spokesman intro
    '\r   「我是 Armun，本族的代言人。'
    '當然，我們知道通出此地各出口的位置，'
    '但在這危急時刻，我無暇相助。'
    '不過，倘若你們願意幫忙我們對付我們的敵人，'
    '我願與你們分享情報。」 ',
    # [4] Armun's long history (1813 bytes — major lore dump)
    '\r   Armun 開口道：「我們族人是建造這些雄偉殿堂的矮人後裔。'
    '我們的祖先曾在此和平居住，直至邪惡生物大舉湧入，'
    '將他們逐入人與精靈之境。\r'
    '   「但我們對昔日榮光的記憶從未磨滅，'
    '族人決意重返這些殿堂，重建家園。'
    '我們從水深市底之地獄地洞展開旅程，'
    '一路殺出血路，奪回更深層的廳堂與舊家。\r'
    '   「然而當我們抵達此處，發現此地早已被卓爾女祭司 Shindia 及其族人占領。'
    '經過漫長激戰，我們以為已將她們驅逐，'
    '但她們最近又重返，並設下一場致命的伏擊。'
    '在戰鬥中，我們的國王 Teirgoh 身受重傷，'
    '更糟的是，她們綁走了王子 Keirgar。\r'
    '   「現在國王命懸一線，王子下落不明，'
    '我們陷入最低潮。'
    '若你們能找到 Shindia 並設法救出王子，'
    '我們將永遠感激你們的協助。'
    '此外，找到能救醒國王的方法亦是當務之急。」 ',
    # [5] Armun disappointment
    '\r   Armun 的表情從期盼轉為沉痛。'
    '「真遺憾你們無法相助。願諸位旅途順利。」 ',
    # [6] Armun accepts help + stone medallion
    '\r   Armun 感激地接受你們的幫助。他交給你們一塊石製徽章。'
    '「拿著這個。Shindia 在那場戰役中遺落的。'
    '它是啟動傳送門的鑰匙，她和她的爪牙就是從那道門逃走的。'
    '門位於此層的某處 — 你們得自行找出來。\r'
    '   「準備好了再來見我。'
    '我會請我們的牧師為你們治療。'
    '此外，請尋找能救醒我們國王的方法。\r'
    '   「最後祝你們狩獵順利。」 ',
    # [7] Armun introduces young warrior
    '\r   Armun 喚住你們。「還有一件事：'
    '一位年輕的矮人戰士想加入你們，'
    '一同尋找王子。你們可以讓他同行嗎？」 ',
    # [8] injured dwarf
    '\r   一名受傷的矮人躺在你們面前，因傷勢而幾近昏迷。 ',
    # [9] weary dwarven cleric
    '\r   一位疲憊的矮人牧師迎接你們。'
    '「請問，有何能為您效勞？」 ',
    # [10] who to resurrect
    '\r   「我該復活何人？」 ',
    # [11] exhausted cleric rest
    '\r   筋疲力盡的矮人牧師揉著眼睛，'
    '請你們待他休息過後再回來。 ',
    # [12] dwarf thanks after rest
    '\r   恢復力氣後，矮人感謝你們。'
    '「我以為自己將死於那卓爾的劍下。'
    '戰鬥中我們的國王重傷，年幼的王子被擄走。'
    '我曾試圖追擊，卻被擊潰。\r'
    '   「拜託，幫我們救出王子，醫好國王。'
    '我們會永遠感念你們。」 ',
    # [13] reconsider offer
    '\r   「你們重新考慮過我們的提議嗎？'
    '雙方合作對我們兩方都有利。」 ',
    # [14] Shindia begs
    '\r   Shindia 突然意識到形勢，懇求饒命。'
    '「等等！別殺我！'
    '我知道很多事，我能告訴你們重要的情報！'
    '我能告訴你們如何救醒國王！'
    '這值得我這條命，不是嗎？」 ',
    # [15] Shindia confession (552 bytes — plot)
    '\r   Shindia 急於保命，把故事和盤托出。'
    '「顯然你們已知曉 Xanathar 的陰謀。'
    '他綁架 Keirgar 王子，'
    '是為了挑撥卓爾和矮人互相殘殺。\r'
    '   「因為我們知道矮人的喜好習性，他派我們去攻擊。'
    '計畫是讓矮人以為是我們綁了王子，'
    '從而使他們對我們宣戰。'
    '當雙方因戰爭兩敗俱傷時，'
    'Xanathar 便能輕鬆奪取兩個王國。\r'
    '   「至於醫治國王，'
    '我聽說有種特殊的矮人解毒藥水可以辦到。」 ',
    # [16] Xanathar speaks (534 bytes — boss monologue)
    '\r   「原來，儘管我設下重重陷阱，'
    '你們這些水深市諸領主的小爪牙還是來到了這裡。'
    '對你們真是不幸啊。」\r'
    '   「對我也甚是悲哀。'
    '我曾極為享受地觀看你們與我的部下交手。'
    '你們的隊伍如此年輕，如此充滿希望。'
    '可惜，今日是你們最後一日。」\r'
    '   「不過，作為觀眾，你們表現得相當出色。'
    '我會在我的紀念冊中為你們留下一頁，'
    '緊接其他試圖阻止 Beholder 老爺的可悲冒險者之後。」 ',
    # [17] vision wavers
    '\r   你們的視野搖晃，一股深刻的虛弱感襲來。'
    '你們覺得不得不丟下一些隨身物品。 ',
    # [18] drow patrol stops you
    '\r   一支卓爾巡邏隊攔住你們的去路。'
    '巡邏隊長以鄙夷的目光打量你們，咆哮道：'
    '「好啊，山怪餵食料們，'
    '給我一個不該把你們送去奴隸營的理由。」 ',
    # [19] patrol leader wants slaves
    '\r   「什麼？你們是想賄賂或羞辱我嗎？'
    '我不要玩具，我要的是潛在的奴隸。'
    '任何生物都行：鳥人、地精、洞穴蜥蜴人。'
    '越年幼越容易馴服。'
    '若你們找得到這類獵物，'
    '我或許願意通融讓你們通過。」 ',
    # [20] kenku egg accepted
    '\r   巡邏隊長拎起一顆鳥人蛋表示滿意。'
    '「年紀小了點，但仍有潛力。\r'
    '   他的黑色目光回到你們身上。「好吧，你們可以通過。'
    '但別擋我們的路！」\r'
    '   卓爾巡邏隊大步離去。 ',
    # [21] dark-robed Xanathar minion (1654 bytes)
    '\r   你們撞見一個身披黑袍的人影。'
    '他先是吃驚，繼而冷笑著認出你們。'
    '「噢，是你們呀。水深市的本週救世主。'
    '你們不知道有多少冒險者被派來探索此事，'
    '同樣，你們也不知道他們最終下場如何。'
    '但這次與從前不同。\r'
    '   「我為什麼要告訴你們？'
    '因為一旦我把你們殺光，那就無所謂了。\r'
    '   「Xanathar 大人對水深市諸領主插手他的計畫已感到不耐。'
    '原本他打算用矮人與卓爾的戰爭吞食水深市的注意力，'
    '在城市混亂之際接管。'
    '現在他打算直接攻擊水深市。\r'
    '   「然而水深市諸領主也不是省油的燈。'
    '他們已聚集了一支精銳的衛隊在城市出入口，'
    '預備迎戰任何膽敢冒出的怪物。'
    '而 Xanathar 大人也已為這場戰鬥作了準備：'
    '他召集了從深淵中喚出的最強勁的盟友，'
    '組成了空前龐大的怪物大軍。\r'
    '   「就算你們能殺到 Xanathar 大人面前，又能怎樣？'
    '他早已備妥每一個可能戰場的防禦。\r'
    '   「夠了，閒談時間結束。'
    '是時候讓你們，水深市的勇士們，'
    '加入過去那些失敗者的行列了！」 ',
    # [22] Prince Keirgar bound
    '\r   你們看到 Keirgar 王子在束縛中掙扎。'
    '他抬頭望向你們，眼神充滿絕望中的希望。'
    '「拜託！你們必須救我出去！'
    '我必須回到我的族人那裡，避免矮人與卓爾之間的戰爭。'
    '時間緊迫！」 ',
    # [23] Taghor joins
    '\r   Taghor 加入隊伍時說道：'
    '「戰鬥中，我追擊敵人上樓，到了這層。'
    '我的族人應該就在我們下層。」 ',
    # [24] dwarven cleric eyes you
    '\r   一位警戒的矮人牧師打量著你們，'
    '說道：「對任何受傷者我都願伸出援手，'
    '但我的族人需要立即的照顧。'
    '當然，如果你們協助我們尋找王子，'
    '情況又會不同。」 ',
    # [25] dwarves rejoice prince return
    '\r   矮人們因王子的歸來而歡欣鼓舞。'
    '戰士與牧師簇擁著王子。'
    'Armun 轉向你們：'
    '「在絕望之中，你們居然帶回了 Keirgar 王子。'
    '我們該如何感謝你們？\r'
    '   「請接受我們的這位戰士的協助，'
    '直到你們達成你們的使命。\r'
    '   「願偉大的矮人之神 Moradin 與你們同在！」 ',
    # [26] Prince Keirgar offers help
    '\r   Keirgar 王子說：'
    '「我必須以其他方式報答你們把我帶回族人之恩。'
    '最起碼我能繼續協助你們對抗 Xanathar。」 ',
    # [27] Keirgar warns plot (714 bytes)
    '\r   Keirgar 王子鬆了一口氣，'
    '「謝謝你們及時救我。現在我必須趕去警告族人兩個惡毒陷阱。\r'
    '   「首先，卓爾族並非我綁架案的真凶。'
    '是 Xanathar 在背後操控，他想挑撥兩族開戰。'
    '我必須阻止族人對卓爾發動仇殺。\r'
    '   「其次，我必須警告族人：'
    'Xanathar 已準備好攻擊矮人王國本身。'
    '他召集了大批怪物，計畫摧毀我們僅存的家園。\r'
    '   「我必須立刻去警告族人。'
    '至於你們，我相信你們能找到 Xanathar 並阻止他。」 ',
    # [28] king awakens (538 bytes)
    '\r   「這應該能救醒國王！」你們交藥水給牧師時喊道。'
    '牧師懷疑地將藥水餵下。'
    '幾刻過後，Teirgoh 國王甦醒，'
    '依然虛弱但無疑活著。\r'
    '   國王感激地說：'
    '「謝謝你們，異鄉的勇者們。'
    '不僅救了我的命，更救了我的兒子和族人。'
    '我能以何相報？\r'
    '   「拿這把矮人鑰匙吧。'
    '它能為你們開啟此地殿堂中的許多門。'
    '願 Moradin 護佑你們的旅程。」 ',
    # [29] Dorhum joins
    '\r   Dorhum 加入隊伍。 ',
    # [30] Dorhum stays
    '\r   Dorhum 不情願地留下，與族人為伍。 ',
    # [31] kill helpless dwarf
    '\r   你們殺了那無助的矮人。 ',
    # [32] Anya confused
    '\r   Anya 困惑地環顧四周。'
    '「我與同伴對抗 Xanathar 的爪牙時陣亡。'
    '我以為會在彼世醒來，'
    '不是在我倒下的地牢之中。」\r'
    '   「我不喜歡此地，但既然你們救了我，'
    '我會盡我所能與你們同行，'
    '直到我們離開此處或我為了我的同袍復仇。」 ',
    # [33] "Hunter's luck" departure
    '\r   「那麼我們的道路必須分歧。'
    '我會對 Xanathar 索取我自己的仇。'
    '願獵者之運引導你們。」 ',
    # [34] Beohram resurrected (313 bytes)
    '\r   Beohram 沉默地低頭嘆息。'
    '「復活了！那我的任務算是失敗了。'
    '我是 City Watch 的 Beohram。'
    '當 Xanathar 的傳聞最初傳出，'
    '我獨自下來調查。'
    '我看得出他們所言不虛。\r'
    '   「我會跟著你們，至少到我能離開此地。'
    '若你們在路上需要幫助對抗 Xanathar，'
    '我會盡力相助。」 ',
    # [35] cannot accompany
    '\r   「很遺憾我無法陪你們去面對那威脅。'
    '當然，這是你們的決定。'
    '我會試著找出自己的出路，'
    '到地面後我會傳唱你們在邪惡面前的英勇事蹟。」 ',
    # [36] Kirath annoyed (428 bytes)
    '\r   Kirath 不悅地環顧。'
    '「你們是說我死了？哼。'
    '現在你大概以為我欠你們復活之恩。'
    '我才不在乎你們從水深市諸領主領的委任，'
    '但我們似乎都往同個方向前進，'
    '所以我會與你們同行，直到我們利益不再相合為止。」\r'
    '   「我提醒你們：別擋我的路。'
    '我為了金子和魔法物品而冒險，'
    '不為了什麼高尚的使命。'
    '如果我能在你們的努力中順手取得一點戰利品，'
    '我會勉強感激。」 ',
    # [37] my way
    '\r   「隨你便。'
    '我或許沒有你們擋路反而更好。」 ',
    # [38] Ileira jubilant (392 bytes)
    '\r   Ileira 喜不自勝地環顧。'
    '「願諸神受讚揚！我是 Ileira 修女。'
    '我與我的同袍下入這些地牢，'
    '為了打擊邪惡並帶來良善。'
    '可惜我們寡不敵眾，多數同袍喪命。\r'
    '   「我會與你們同行，協助你們的志業。'
    '光明的諸神必定眷顧你們的努力。'
    '此外，能成為與如此勇敢冒險者同行的牧師，'
    '是我莫大的榮幸。」 ',
    # [39] seek my own path
    '\r   「那麼我必須尋找自己的道路。'
    '願諸位平安，願光明引導你們。」 ',
    # [40] Tyrra cynical (443 bytes)
    '\r   Tyrra 環顧四周。'
    '「啊，這真是太棒了。'
    '我跟著某個白癡隊伍下來這裡被殺，'
    '現在又有另一隊伍經過，把我復活，'
    '還要我加入！就這樣！\r'
    '   「好吧，反正我也沒別的計畫。'
    '我會跟你們走，但有條件：'
    '我們找到的所有寶藏我都分一份。'
    '此外，我不接受命令，只接受合作建議。」 ',
    # [41] just for fun
    '\r   「所以你們把我復活只是為了好玩？'
    '當然，去吧。我沒意見。'
    '你們想做什麼隨你們便。'
    '至於我，我自己會找出路。」 ',
    # [42] Tod halfling (344 bytes)
    '\r   Tod 疲憊地環顧四周。'
    '「我...我不太清楚自己怎麼會下來這裡。'
    '你們說我死了？'
    '我最後的記憶是跌入下水道之一。\r'
    '   「喂，這可不好笑！'
    '我可是個正經的冒險家。'
    '我曾被委以多項重大任務。'
    '或許你們的隊伍能用得上一個熟練的盜賊？」 ',
    # [43] halfling shrugs off
    '\r   半身人聳聳肩。'
    '當他走開時，他喃喃低語：'
    '「你們的損失...傻瓜。」 ',
    # [44] Keirgar joins
    '\r   Keirgar 加入隊伍。 ',
    # [45] Keirgar wanders off
    '\r   Keirgar 為尋找族人而離去。 ',
    # [46] Commission and Letter of Marque
    '委任狀及私掠許可：\r'
    '\r此文件為效力於海岸城邦水深市諸領主之約束委任。'
    '持此文件者乃水深市諸領主之代理人，'
    '獲准全權通行於水深市底之領域。'
    '凡膽敢阻撓者，將承受我等怒火之全部懲罰。',
    # [47] Riddle 1
    '\r   星辰之光於寶石中閃爍。\r   循其一以見其二。 ',
    # [48] Riddle 2
    '\r   頸上以金鑄就\r   矮人之印\r   已告知爾等 ',
    # [49] Riddle 3
    '\r   此球通往大邪惡。 ',
    # [50] Riddle 4
    '\r   最令人懼怕的生物，其最大弱點在於：'
    '雖潛伏陰影中、目視萬物，'
    '卻無法令自身隱形。 ',
    # [51] Epilogue
    '\r   隊伍在 Xanathar 殘破軀體的廢墟中翻找之際，'
    '一座傳送器在四周啟動。'
    '當 Xanathar 巢穴從視野中消逝，'
    '眾人皆已備戰，思忖：「現在又如何？」\r'
    '   一座莊嚴的大理石殿堂於眾人周遭浮現。\r'
    '   兩根石柱拱衛著一張巨大的王座。'
    '陽光透入...\r'
    '\r   水深市諸領主歡迎你們的歸來，'
    '感激你們挫敗了 Xanathar 的陰謀。'
    '水深市以及矮人王國對於你們的英勇將永誌不忘。',
]

assert len(ZH) == 51, f"Got {len(ZH)} translations, expected 51"


def encode_zh(s):
    try:
        return s.encode('cp950')
    except UnicodeEncodeError as e:
        print(f"cp950 encode FAIL: {e}", file=sys.stderr)
        # Replace bad chars with '?'
        return s.encode('cp950', errors='replace')


# Build new strings
new_strings_bytes = [encode_zh(s) + b'\0' for s in ZH]

n = len(new_strings_bytes)
table_size = n * 2
new_offsets = []
cur = table_size
for sb in new_strings_bytes:
    new_offsets.append(cur)
    cur += len(sb)

total_size = cur
print(f"New TEXT.DAT size: {total_size} bytes (was {len(orig)})", file=sys.stderr)

# Sanity: total < 32000 (engine reads max 32000 to page 5)
if total_size > 32000:
    print(f"WARN: total {total_size} > 32000 — engine truncates", file=sys.stderr)

# Per-string size check (engine has no per-string max, but reasonable < 2000)
max_len = max(len(s) for s in new_strings_bytes)
print(f"Max single string size: {max_len} bytes", file=sys.stderr)

# Build buffer
buf = bytearray()
for o in new_offsets:
    buf += struct.pack('<H', o)
for sb in new_strings_bytes:
    buf += sb

assert len(buf) == total_size

OUT_GAME.write_bytes(bytes(buf))
OUT_BACKUP.write_bytes(bytes(buf))
print(f"Wrote {OUT_GAME} ({len(buf)} bytes)", file=sys.stderr)

# Verify a few entries via re-parse
print(f"\n=== Verification: 5 sample entries ===", file=sys.stderr)
for i in [0, 3, 15, 45, 50]:
    o = new_offsets[i]
    end = buf.find(0, o)
    s = bytes(buf[o:end]).decode('cp950', errors='replace')
    preview = s if len(s) < 100 else s[:100] + '...'
    print(f"[{i+1}] @ {o:04x} ({end-o} B): {preview}", file=sys.stderr)
